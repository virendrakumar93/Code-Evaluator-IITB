"""Consistency checking and hallucination auditing."""

from __future__ import annotations

import logging
from dataclasses import asdict

from evaluator.schema import (
    EvaluationResult,
    ExecutionArtifact,
    LLMJudgment,
    RubricScores,
)

logger = logging.getLogger(__name__)


def check_consistency(
    result1: EvaluationResult,
    result2: EvaluationResult,
    tolerance: float = 0.5,
) -> dict:
    """
    Compare two evaluation runs for the same submission.

    Returns consistency report with per-dimension agreement.
    """
    s1 = result1.llm_judgment.scores
    s2 = result2.llm_judgment.scores

    dimensions = ["correctness", "edge_cases", "complexity", "style", "clarity"]
    differences = {}
    consistent = True

    for dim in dimensions:
        v1 = getattr(s1, dim)
        v2 = getattr(s2, dim)
        diff = abs(v1 - v2)
        differences[dim] = {
            "run1": v1,
            "run2": v2,
            "difference": round(diff, 2),
            "consistent": diff <= tolerance,
        }
        if diff > tolerance:
            consistent = False

    det_diff = abs(result1.deterministic_score - result2.deterministic_score)

    return {
        "consistent": consistent,
        "tolerance": tolerance,
        "dimension_differences": differences,
        "deterministic_diff": round(det_diff, 4),
        "deterministic_consistent": det_diff < 0.01,
        "final_score_diff": round(
            abs(result1.final_score - result2.final_score), 4
        ),
    }


def audit_hallucinations(
    artifact: ExecutionArtifact,
    judgment: LLMJudgment,
) -> list[str]:
    """
    Audit LLM judgment for hallucinations - claims not grounded in evidence.

    Returns list of hallucination flags.
    """
    flags = []

    # 1. Check correctness claims vs test results
    if judgment.scores.correctness > 7.0 and artifact.test_results.pass_rate < 0.7:
        flags.append(
            f"HALLUCINATION: LLM claims high correctness ({judgment.scores.correctness}) "
            f"but test pass rate is only {artifact.test_results.pass_rate:.0%}"
        )

    if judgment.scores.correctness < 3.0 and artifact.test_results.pass_rate > 0.9:
        flags.append(
            f"HALLUCINATION: LLM claims low correctness ({judgment.scores.correctness}) "
            f"but test pass rate is {artifact.test_results.pass_rate:.0%}"
        )

    # 2. Check edge case claims vs test results
    if judgment.scores.edge_cases > 8.0 and artifact.test_results.pass_rate < 0.8:
        flags.append(
            f"HALLUCINATION: LLM claims good edge case handling ({judgment.scores.edge_cases}) "
            f"but overall pass rate is {artifact.test_results.pass_rate:.0%}"
        )

    # 3. Check style claims vs static analysis
    warning_count = len([w for w in artifact.static_warnings if w.rule != "TOOL_ERROR"])
    if judgment.scores.style > 8.0 and warning_count > 5:
        flags.append(
            f"HALLUCINATION: LLM claims good style ({judgment.scores.style}) "
            f"but there are {warning_count} static analysis warnings"
        )

    if judgment.scores.style < 3.0 and warning_count == 0:
        flags.append(
            f"HALLUCINATION: LLM claims poor style ({judgment.scores.style}) "
            f"but there are no static analysis warnings"
        )

    # 4. Check claims without evidence
    if judgment.confidence > 0.8 and len(judgment.evidence_used) < 2:
        flags.append(
            f"SUSPICIOUS: High confidence ({judgment.confidence}) "
            f"with only {len(judgment.evidence_used)} evidence sources"
        )

    # 5. Check for timeout/sandbox issues ignored
    if artifact.timeout and judgment.scores.correctness > 2.0:
        flags.append(
            "HALLUCINATION: LLM gives correctness score despite code timeout"
        )

    if artifact.sandbox_violation and judgment.scores.correctness > 0.0:
        flags.append(
            "HALLUCINATION: LLM gives correctness score despite sandbox violation"
        )

    # 6. Check if issues list is empty when there are clear problems
    if artifact.test_results.failed > 0 and len(judgment.issues) == 0:
        flags.append(
            f"SUSPICIOUS: No issues reported but {artifact.test_results.failed} tests failed"
        )

    return flags


def compute_grader_accuracy(
    predicted_scores: list[dict],
    gold_scores: list[dict],
) -> dict:
    """
    Compute grader accuracy metrics against gold standard.

    Returns MAE, exact match %, and correlation per dimension.
    """
    dimensions = ["correctness", "edge_cases", "complexity", "style", "clarity", "overall"]

    metrics = {}

    for dim in dimensions:
        pred_vals = []
        gold_vals = []

        for pred, gold in zip(predicted_scores, gold_scores):
            if dim in pred and dim in gold:
                pred_vals.append(float(pred[dim]))
                gold_vals.append(float(gold[dim]))

        if not pred_vals:
            continue

        n = len(pred_vals)

        # MAE
        mae = sum(abs(p - g) for p, g in zip(pred_vals, gold_vals)) / n

        # Exact match (within tolerance of 0.5)
        exact = sum(1 for p, g in zip(pred_vals, gold_vals) if abs(p - g) <= 0.5)
        exact_pct = exact / n * 100

        # Pearson correlation
        mean_p = sum(pred_vals) / n
        mean_g = sum(gold_vals) / n

        cov = sum((p - mean_p) * (g - mean_g) for p, g in zip(pred_vals, gold_vals)) / n
        std_p = (sum((p - mean_p) ** 2 for p in pred_vals) / n) ** 0.5
        std_g = (sum((g - mean_g) ** 2 for g in gold_vals) / n) ** 0.5

        if std_p > 0 and std_g > 0:
            correlation = cov / (std_p * std_g)
        else:
            correlation = 0.0

        metrics[dim] = {
            "mae": round(mae, 4),
            "exact_match_pct": round(exact_pct, 2),
            "correlation": round(correlation, 4),
            "n": n,
        }

    return metrics
