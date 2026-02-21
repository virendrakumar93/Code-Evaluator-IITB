"""LLM-based judge using HuggingFace Inference API (via huggingface_hub)."""

from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import asdict
from huggingface_hub import InferenceClient
from evaluator.schema import (
    ExecutionArtifact,
    LLMJudgment,
    RubricScores,
    StaticWarning,
    TestSuiteResult,
)
from evaluator.sandbox import strip_comments

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "Qwen/Qwen2.5-Coder-7B-Instruct"
FALLBACK_MODELS = [
    "Qwen/Qwen2.5-Coder-1.5B-Instruct",
    "bigcode/starcoder2-15b",
]

GRADING_PROMPT_TEMPLATE = """\
You are an expert code evaluator. You MUST evaluate the following code submission \
based STRICTLY on the provided evidence. You are NOT allowed to make claims \
without supporting evidence. If evidence is missing, say "insufficient evidence."

## Problem Statement
{problem_statement}

## Submission Code (sanitized)
```python
{sanitized_code}
```

## Reference Solution
```python
{reference_code}
```

## Test Results Evidence
- Total tests: {total_tests}
- Passed: {passed_tests}
- Failed: {failed_tests}
- Errors: {error_tests}
- Pass rate: {pass_rate}
- Execution time: {execution_time}s
- Timeout: {timeout}
- Sandbox violation: {sandbox_violation}

### Failed Test Details:
{failed_details}

## Static Analysis Evidence
- Total warnings: {total_warnings}
- Warning details:
{warning_details}

## Deterministic Scores (pre-computed)
- Correctness: {det_correctness}/10
- Edge Cases: {det_edge_cases}/10
- Complexity: {det_complexity}/10
- Style: {det_style}/10
- Clarity: {det_clarity}/10

## Instructions
Evaluate the submission and provide scores on a 0-10 scale for each rubric dimension.
You MUST ground your scores in the evidence above. Do NOT make claims about behavior \
not verified by tests. If test evidence is missing for a claim, flag it as uncertain.

Your scores should generally align with the deterministic scores but you may adjust \
them based on your analysis of code quality, approach, and reasoning. Adjustments \
should be within +/- 2 points of deterministic scores and must be justified.

CRITICAL RULES:
1. Do NOT claim the code is correct if tests fail.
2. Do NOT claim edge cases are handled if no edge case tests pass.
3. Do NOT claim good complexity without reasoning about the algorithm.
4. Flag any uncertainty explicitly.
5. If evidence is insufficient, state that clearly.

Respond ONLY with valid JSON in this exact format:
{{
    "scores": {{
        "correctness": <float 0-10>,
        "edge_cases": <float 0-10>,
        "complexity": <float 0-10>,
        "style": <float 0-10>,
        "clarity": <float 0-10>
    }},
    "issues": ["<issue1>", "<issue2>"],
    "suggestions": ["<suggestion1>", "<suggestion2>"],
    "evidence_used": ["<evidence reference1>", "<evidence reference2>"],
    "confidence": <float 0-1>,
    "uncertainty_flags": ["<flag1 if any>"]
}}
"""


def _get_api_token() -> str:
    """Get HuggingFace API token from environment."""
    token = os.environ.get("HF_TOKEN") or os.environ.get("HF_API_KEY") or os.environ.get("HUGGINGFACE_API_KEY")
    if not token:
        raise EnvironmentError(
            "HuggingFace API token not found. Set HF_TOKEN in .env"
        )
    return token

def _create_client(model: str, token: str) -> InferenceClient:
    """Create a HuggingFace InferenceClient."""
    return InferenceClient(model=model, token=token, timeout=120)

def _call_hf_api(prompt: str, model: str, api_token: str, max_tokens: int = 2048) -> str:
    """Call HuggingFace Inference API via official InferenceClient."""
    client = _create_client(model, api_token)
    for attempt in range(2):
        try:
            result = client.text_generation(
                prompt,
                max_new_tokens=max_tokens,
                temperature=0.1,
                do_sample=False,
                return_full_text=False,
            )
            return result
        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg or "loading" in error_msg.lower():
                logger.info("Model loading, waiting 30s...")
                time.sleep(30)
                continue
            raise

     raise RuntimeError(f"Model {model} failed to respond after retries")


def _parse_llm_response(response_text: str) -> dict | None:
    """Extract and parse JSON from LLM response."""
    # Try to find JSON block
    json_match = re.search(r"\{[\s\S]*\}", response_text)
    if json_match:
        try:
            data = json.loads(json_match.group())
            # Validate required fields
            if "scores" in data and isinstance(data["scores"], dict):
                required = {"correctness", "edge_cases", "complexity", "style", "clarity"}
                if required.issubset(data["scores"].keys()):
                    return data
        except json.JSONDecodeError:
            pass
    return None


def _clamp(val: float, lo: float = 0.0, hi: float = 10.0) -> float:
    return round(max(lo, min(hi, float(val))), 2)


def build_grading_prompt(
    problem_statement: str,
    submission_code: str,
    reference_code: str,
    artifact: ExecutionArtifact,
    deterministic_scores: RubricScores,
) -> str:
    """Build the full grading prompt with evidence."""
    sanitized = strip_comments(submission_code)

    failed_details = ""
    for r in artifact.test_results.results:
        if not r.passed:
            msg = r.message[:200] if r.message else "No details"
            failed_details += f"- {r.test_name}: {msg}\n"
    if not failed_details:
        failed_details = "None - all tests passed."

    warning_details = ""
    for w in artifact.static_warnings:
        warning_details += f"- [{w.rule}] Line {w.line}: {w.message}\n"
    if not warning_details:
        warning_details = "None - no warnings."

    return GRADING_PROMPT_TEMPLATE.format(
        problem_statement=problem_statement,
        sanitized_code=sanitized,
        reference_code=reference_code,
        total_tests=artifact.test_results.total,
        passed_tests=artifact.test_results.passed,
        failed_tests=artifact.test_results.failed,
        error_tests=artifact.test_results.errors,
        pass_rate=artifact.test_results.pass_rate,
        execution_time=artifact.execution_time,
        timeout=artifact.timeout,
        sandbox_violation=artifact.sandbox_violation,
        failed_details=failed_details,
        total_warnings=len(artifact.static_warnings),
        warning_details=warning_details,
        det_correctness=deterministic_scores.correctness,
        det_edge_cases=deterministic_scores.edge_cases,
        det_complexity=deterministic_scores.complexity,
        det_style=deterministic_scores.style,
        det_clarity=deterministic_scores.clarity,
    )


def judge_submission(
    problem_statement: str,
    submission_code: str,
    reference_code: str,
    artifact: ExecutionArtifact,
    deterministic_scores: RubricScores,
    model: str | None = None,
) -> LLMJudgment:
    """
    Use LLM to evaluate a submission with evidence grounding.

    Retries once on malformed output. Falls back to deterministic scores
    if LLM fails entirely.
    """
    model = model or DEFAULT_MODEL

    try:
        api_token = _get_api_token()
    except EnvironmentError as e:
         logger.warning(f"No API token: {e}. Using deterministic scores only.")
        return _fallback_judgment(deterministic_scores)

    prompt = build_grading_prompt(
        problem_statement,
        submission_code,
        reference_code,
        artifact,
        deterministic_scores,
    )

    # Try primary model with one retry
    for attempt in range(2):
        try:
            response_text = _call_hf_api(prompt, model, api_token)
            parsed = _parse_llm_response(response_text)

            if parsed is not None:
                return _build_judgment(parsed, response_text, deterministic_scores)

            logger.warning(
                f"Attempt {attempt + 1}: Malformed LLM output, "
                f"{'retrying' if attempt == 0 else 'falling back'}"
            )

        except Exception as e:
            logger.warning(f"LLM API error (attempt {attempt + 1}): {e}")

    # Try fallback models
    for fb_model in FALLBACK_MODELS:
        try:
            response_text = _call_hf_api(prompt, fb_model, api_token)
            parsed = _parse_llm_response(response_text)
            if parsed is not None:
                return _build_judgment(parsed, response_text, deterministic_scores)
        except Exception as e:
            logger.warning(f"Fallback model {fb_model} failed: {e}")

    logger.warning("All LLM attempts failed. Using deterministic scores.")
    return _fallback_judgment(deterministic_scores)


def _build_judgment(
    parsed: dict, raw_response: str, det_scores: RubricScores
) -> LLMJudgment:
    """Build LLMJudgment from parsed response, clamping scores."""
    scores = parsed["scores"]

    # Clamp scores to be within reasonable range of deterministic
    llm_scores = RubricScores(
        correctness=_clamp(scores.get("correctness", det_scores.correctness)),
        edge_cases=_clamp(scores.get("edge_cases", det_scores.edge_cases)),
        complexity=_clamp(scores.get("complexity", det_scores.complexity)),
        style=_clamp(scores.get("style", det_scores.style)),
        clarity=_clamp(scores.get("clarity", det_scores.clarity)),
    )

    return LLMJudgment(
        scores=llm_scores,
        issues=parsed.get("issues", []),
        suggestions=parsed.get("suggestions", []),
        evidence_used=parsed.get("evidence_used", []),
        confidence=_clamp(parsed.get("confidence", 0.5), 0.0, 1.0),
        uncertainty_flags=parsed.get("uncertainty_flags", []),
        raw_response=raw_response[:2000],
    )


def _fallback_judgment(det_scores: RubricScores) -> LLMJudgment:
    """Create fallback judgment using only deterministic scores."""
    return LLMJudgment(
        scores=det_scores,
        issues=["LLM evaluation unavailable - using deterministic scores only"],
        suggestions=[],
        evidence_used=["deterministic_test_results", "static_analysis"],
        confidence=0.3,
        uncertainty_flags=["llm_fallback_mode"],
        raw_response="",
    )
