"""LLM-based judge using HuggingFace Inference API (chat completions).

Architecture decision: Uses chat_completion API (conversational task) instead
of legacy text_generation to ensure compatibility with modern inference
providers (e.g., nscale). Falls back to text_generation only when the
conversational task is unavailable for a given model.

Key fixes over original:
  1. Indentation bug on fallback return — now correctly inside except block
  2. Switched from text_generation to chat_completion (provider-compatible)
  3. Capability-aware routing via HuggingFace model metadata API
  4. Separated system/user prompts for proper chat API usage
"""

from __future__ import annotations

import json
import logging
import os
import re
import time

import requests as http_requests
from huggingface_hub import InferenceClient

from evaluator.schema import (
    ExecutionArtifact,
    LLMJudgment,
    RubricScores,
)
from evaluator.sandbox import strip_comments

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "Qwen/Qwen2.5-Coder-7B-Instruct"
FALLBACK_MODELS = [
    "Qwen/Qwen2.5-Coder-1.5B-Instruct",
    "bigcode/starcoder2-15b",
]

# Capability cache: avoids repeated metadata queries for the same model
_capability_cache: dict[str, set[str]] = {}


# ---------------------------------------------------------------------------
# Prompt Templates
# ---------------------------------------------------------------------------
# Separated into system + user for the chat completion API.
# System prompt: evaluator role and hard constraints.
# User prompt: evidence payload and output schema.

SYSTEM_PROMPT = """\
You are an expert code evaluator. You MUST evaluate code submissions based \
STRICTLY on the provided evidence. You are NOT allowed to make claims \
without supporting evidence. If evidence is missing, say "insufficient evidence."

CRITICAL RULES:
1. Do NOT claim the code is correct if tests fail.
2. Do NOT claim edge cases are handled if no edge case tests pass.
3. Do NOT claim good complexity without reasoning about the algorithm.
4. Flag any uncertainty explicitly.
5. If evidence is insufficient, state that clearly.

You MUST respond ONLY with valid JSON matching the requested schema. \
No markdown fences, no explanation outside the JSON object."""

USER_PROMPT_TEMPLATE = """\
Evaluate the following code submission based on the evidence below.

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

## Task
Provide scores on a 0-10 scale for each rubric dimension. Ground your scores \
in the evidence above. Adjustments from deterministic scores should be within \
+/- 2 points and must be justified.

Respond with valid JSON in this exact format:
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
}}"""


# ---------------------------------------------------------------------------
# API Token
# ---------------------------------------------------------------------------

def _get_api_token() -> str:
    """Get HuggingFace API token from environment."""
    token = (
        os.environ.get("HF_TOKEN")
        or os.environ.get("HF_API_KEY")
        or os.environ.get("HUGGINGFACE_API_KEY")
    )
    if not token:
        raise EnvironmentError(
            "HuggingFace API token not found. Set HF_TOKEN in .env"
        )
    return token


# ---------------------------------------------------------------------------
# Capability Detection
# ---------------------------------------------------------------------------

def _query_model_tasks(model: str, api_token: str) -> set[str]:
    """
    Query HuggingFace model metadata for supported inference tasks.

    Inspects the inferenceProviderMapping to determine which tasks each
    provider supports. Results are cached per-model to avoid repeated calls.
    """
    if model in _capability_cache:
        return _capability_cache[model]

    tasks: set[str] = set()
    try:
        resp = http_requests.get(
            f"https://huggingface.co/api/models/{model}",
            params={"expand": "inferenceProviderMapping"},
            headers={"Authorization": f"Bearer {api_token}"},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            # Extract tasks from each inference provider
            provider_map = data.get("inferenceProviderMapping", {})
            for provider_info in provider_map.values():
                if isinstance(provider_info, dict):
                    task = provider_info.get("task")
                    if task:
                        tasks.add(task)
                elif isinstance(provider_info, str):
                    tasks.add(provider_info)
            # Also include the model's declared pipeline tag
            pipeline_tag = data.get("pipeline_tag", "")
            if pipeline_tag:
                tasks.add(pipeline_tag)
            logger.debug(f"Model {model} supports tasks: {tasks}")
    except Exception as e:
        logger.debug(f"Could not query capabilities for {model}: {e}")

    _capability_cache[model] = tasks
    return tasks


# ---------------------------------------------------------------------------
# API Call Layer
# ---------------------------------------------------------------------------

def _create_client(model: str, token: str) -> InferenceClient:
    """Create a HuggingFace InferenceClient."""
    return InferenceClient(model=model, token=token, timeout=120)


def _call_chat_api(
    system_prompt: str,
    user_prompt: str,
    model: str,
    api_token: str,
    max_tokens: int = 800,
) -> str:
    """Call HuggingFace chat completion API (conversational task)."""
    client = _create_client(model, api_token)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    response = client.chat_completion(
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.2,
    )
    return response.choices[0].message.content


def _call_text_generation(
    prompt: str, model: str, api_token: str, max_tokens: int = 800
) -> str:
    """Legacy text generation API (for models without chat support)."""
    client = _create_client(model, api_token)
    return client.text_generation(
        prompt,
        max_new_tokens=max_tokens,
        temperature=0.1,
        do_sample=False,
        return_full_text=False,
    )


def _invoke_model(
    system_prompt: str,
    user_prompt: str,
    model: str,
    api_token: str,
    max_tokens: int = 800,
) -> str:
    """
    Capability-aware model invocation.

    Routes to the correct API based on model metadata:
      - conversational → chat_completion (preferred)
      - text-generation → text_generation (legacy fallback)
    If metadata is unavailable, tries chat first then text-generation.
    """
    tasks = _query_model_tasks(model, api_token)

    # Route based on detected capabilities
    if tasks:
        if "conversational" in tasks:
            logger.debug(f"Using chat API for {model} (conversational supported)")
            return _call_chat_api(
                system_prompt, user_prompt, model, api_token, max_tokens
            )
        elif "text-generation" in tasks:
            logger.debug(f"Using text-generation API for {model}")
            combined = f"{system_prompt}\n\n{user_prompt}"
            return _call_text_generation(
                combined, model, api_token, max_tokens
            )
        else:
            raise RuntimeError(
                f"Model {model} supports neither conversational nor "
                f"text-generation. Available tasks: {tasks}"
            )

    # Capabilities unknown — try chat first, fall back to text generation
    logger.debug(f"Capabilities unknown for {model}, trying chat API first")
    try:
        return _call_chat_api(
            system_prompt, user_prompt, model, api_token, max_tokens
        )
    except Exception as chat_err:
        err_msg = str(chat_err).lower()
        if "not supported" in err_msg or "task" in err_msg:
            logger.info(
                f"Chat API unavailable for {model}, "
                f"falling back to text-generation"
            )
            combined = f"{system_prompt}\n\n{user_prompt}"
            return _call_text_generation(
                combined, model, api_token, max_tokens
            )
        raise


# ---------------------------------------------------------------------------
# Response Parsing
# ---------------------------------------------------------------------------

def _parse_llm_response(response_text: str) -> dict | None:
    """Extract and parse JSON from LLM response."""
    if not response_text:
        return None
    json_match = re.search(r"\{[\s\S]*\}", response_text)
    if json_match:
        try:
            data = json.loads(json_match.group())
            if "scores" in data and isinstance(data["scores"], dict):
                required = {
                    "correctness", "edge_cases", "complexity",
                    "style", "clarity",
                }
                if required.issubset(data["scores"].keys()):
                    return data
        except json.JSONDecodeError:
            pass
    return None


def _clamp(val: float, lo: float = 0.0, hi: float = 10.0) -> float:
    return round(max(lo, min(hi, float(val))), 2)


# ---------------------------------------------------------------------------
# Prompt Construction
# ---------------------------------------------------------------------------

def build_grading_prompt(
    problem_statement: str,
    submission_code: str,
    reference_code: str,
    artifact: ExecutionArtifact,
    deterministic_scores: RubricScores,
) -> str:
    """Build the user-facing evidence prompt (system prompt is separate)."""
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

    return USER_PROMPT_TEMPLATE.format(
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


# ---------------------------------------------------------------------------
# Evaluation Entry Point
# ---------------------------------------------------------------------------

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

    user_prompt = build_grading_prompt(
        problem_statement,
        submission_code,
        reference_code,
        artifact,
        deterministic_scores,
    )

    # Try primary model with one retry
    for attempt in range(2):
        try:
            response_text = _invoke_model(
                SYSTEM_PROMPT, user_prompt, model, api_token
            )
            parsed = _parse_llm_response(response_text)

            if parsed is not None:
                logger.info(
                    f"LLM evaluation successful "
                    f"(model={model}, attempt={attempt + 1})"
                )
                return _build_judgment(parsed, response_text, deterministic_scores)

            logger.warning(
                f"Attempt {attempt + 1}: Malformed LLM output, "
                f"{'retrying' if attempt == 0 else 'falling back'}"
            )

        except Exception as e:
            error_msg = str(e)
            if "503" in error_msg or "loading" in error_msg.lower():
                logger.info("Model loading, waiting 30s...")
                time.sleep(30)
                continue
            logger.warning(f"LLM API error (attempt {attempt + 1}): {e}")

    # Try fallback models
    for fb_model in FALLBACK_MODELS:
        logger.info(f"Trying fallback model: {fb_model}")
        try:
            response_text = _invoke_model(
                SYSTEM_PROMPT, user_prompt, fb_model, api_token
            )
            parsed = _parse_llm_response(response_text)
            if parsed is not None:
                logger.info(f"Fallback model {fb_model} succeeded")
                return _build_judgment(parsed, response_text, deterministic_scores)
            logger.warning(f"Fallback model {fb_model}: malformed output")
        except Exception as e:
            logger.warning(f"Fallback model {fb_model} failed: {e}")

    logger.warning("All LLM attempts failed. Using deterministic scores.")
    return _fallback_judgment(deterministic_scores)


# ---------------------------------------------------------------------------
# Result Construction
# ---------------------------------------------------------------------------

def _build_judgment(
    parsed: dict, raw_response: str, det_scores: RubricScores
) -> LLMJudgment:
    """Build LLMJudgment from parsed response, clamping scores."""
    scores = parsed["scores"]

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
