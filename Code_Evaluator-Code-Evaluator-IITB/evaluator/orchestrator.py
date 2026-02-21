"""Evaluation orchestrator - coordinates all components."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

import yaml

from evaluator.schema import (
    EvaluationResult,
    ExecutionArtifact,
    GoldScore,
    LLMJudgment,
    RubricScores,
)
from evaluator.test_runner import run_tests
from evaluator.static_analysis import run_static_analysis
from evaluator.rubric_engine import compute_deterministic_scores
from evaluator.llm_judge import judge_submission
from evaluator.consistency_checker import (
    audit_hallucinations,
    check_consistency,
    compute_grader_accuracy,
)

logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> dict:
    """Load pipeline configuration."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def discover_problems(problems_dir: str = "problems") -> list[dict]:
    """Discover all problems in the problems directory."""
    problems = []
    base = Path(problems_dir)

    for pdir in sorted(base.iterdir()):
        if not pdir.is_dir() or pdir.name.startswith("."):
            continue

        desc_path = pdir / "description.md"
        ref_path = pdir / "reference.py"
        test_path = pdir / "tests.py"
        subs_dir = pdir / "submissions"

        if not all(p.exists() for p in [desc_path, ref_path, test_path]):
            logger.warning(f"Skipping {pdir.name}: missing required files")
            continue

        submissions = []
        if subs_dir.exists():
            for sf in sorted(subs_dir.iterdir()):
                if sf.suffix == ".py":
                    submissions.append(sf)

        problems.append({
            "id": pdir.name,
            "description_path": str(desc_path),
            "reference_path": str(ref_path),
            "tests_path": str(test_path),
            "submissions": submissions,
            "dir": str(pdir),
        })

    return problems


def get_function_name(problem_id: str) -> str:
    """Map problem ID to the main function name."""
    mapping = {
        "problem_1": "two_sum",
        "problem_2": "generate_parentheses",
        "problem_3": "climb_stairs",
        "problem_4": "evaluate_expression",
        "problem_5": "shortest_path",
    }
    return mapping.get(problem_id, "solution")


def get_expected_complexity(problem_id: str) -> str:
    """Map problem ID to expected complexity."""
    mapping = {
        "problem_1": "O(n)",
        "problem_2": "O(4^n/sqrt(n))",
        "problem_3": "O(n)",
        "problem_4": "O(n)",
        "problem_5": "O(V+E)",
    }
    return mapping.get(problem_id, "O(n)")


def evaluate_single_submission(
    problem: dict,
    submission_path: Path,
    config: dict,
) -> EvaluationResult:
    """Evaluate a single submission against a problem."""
    problem_id = problem["id"]
    submission_id = submission_path.stem

    logger.info(f"Evaluating {problem_id}/{submission_id}")

    # Read files
    description = Path(problem["description_path"]).read_text()
    reference_code = Path(problem["reference_path"]).read_text()
    test_code = Path(problem["tests_path"]).read_text()
    submission_code = submission_path.read_text()
    function_name = get_function_name(problem_id)

    # Step 1: Run tests in sandbox
    timeout = config.get("sandbox", {}).get("timeout", 3.0)
    test_result, raw_sandbox = run_tests(
        submission_code, test_code, function_name, timeout
    )

    # Step 2: Static analysis
    static_warnings = run_static_analysis(submission_code)

    # Step 3: Build execution artifact
    artifact = ExecutionArtifact(
        test_results=test_result,
        static_warnings=static_warnings,
        runtime_errors=raw_sandbox.get("stderr", "")[:500],
        execution_time=raw_sandbox.get("execution_time", 0.0),
        sandbox_violation=raw_sandbox.get("sandbox_violation", False),
        timeout=raw_sandbox.get("timeout", False),
    )

    # Step 4: Deterministic scoring
    expected_complexity = get_expected_complexity(problem_id)
    det_scores = compute_deterministic_scores(
        submission_code, test_result, static_warnings, expected_complexity
    )

    # Step 5: LLM judgment
    llm_model = config.get("llm", {}).get("model", None)
    use_llm = config.get("llm", {}).get("enabled", True)

    if use_llm:
        llm_judgment = judge_submission(
            problem_statement=description,
            submission_code=submission_code,
            reference_code=reference_code,
            artifact=artifact,
            deterministic_scores=det_scores,
            model=llm_model,
        )
    else:
        from evaluator.llm_judge import _fallback_judgment
        llm_judgment = _fallback_judgment(det_scores)

    # Step 6: Hallucination audit
    hallucination_flags = audit_hallucinations(artifact, llm_judgment)

    # Step 7: Compute final score
    # Blend: 60% deterministic + 40% LLM (if available and confident)
    det_overall = det_scores.overall()
    llm_overall = llm_judgment.scores.overall()

    if llm_judgment.confidence >= 0.5 and not hallucination_flags:
        blend_weight = config.get("scoring", {}).get("llm_weight", 0.4)
        final_score = round(
            det_overall * (1 - blend_weight) + llm_overall * blend_weight, 4
        )
    else:
        final_score = det_overall

    result = EvaluationResult(
        problem_id=problem_id,
        submission_id=submission_id,
        deterministic_score=round(det_overall, 4),
        llm_adjusted_score=round(llm_overall, 4),
        final_score=final_score,
        execution_artifact=artifact,
        llm_judgment=llm_judgment,
        hallucination_flags=hallucination_flags,
    )

    return result


def evaluate_all(config: dict) -> list[EvaluationResult]:
    """Evaluate all submissions for all problems."""
    problems_dir = config.get("paths", {}).get("problems", "problems")
    problems = discover_problems(problems_dir)

    if not problems:
        logger.error("No problems found!")
        return []

    logger.info(f"Found {len(problems)} problems")

    all_results = []

    for problem in problems:
        submissions = problem["submissions"]
        logger.info(
            f"Problem {problem['id']}: {len(submissions)} submissions"
        )

        for sub_path in submissions:
            try:
                result = evaluate_single_submission(problem, sub_path, config)
                all_results.append(result)
                logger.info(
                    f"  {sub_path.stem}: "
                    f"det={result.deterministic_score:.2f} "
                    f"llm={result.llm_adjusted_score:.2f} "
                    f"final={result.final_score:.2f}"
                )
            except Exception as e:
                logger.error(f"  {sub_path.stem}: FAILED - {e}")
                # Create error result
                all_results.append(
                    EvaluationResult(
                        problem_id=problem["id"],
                        submission_id=sub_path.stem,
                        hallucination_flags=[f"Evaluation error: {e}"],
                    )
                )

    return all_results


def run_consistency_check(
    config: dict, sample_size: int = 5
) -> list[dict]:
    """Run evaluation twice on a sample and check consistency."""
    problems_dir = config.get("paths", {}).get("problems", "problems")
    problems = discover_problems(problems_dir)

    consistency_results = []
    count = 0

    for problem in problems:
        for sub_path in problem["submissions"]:
            if count >= sample_size:
                break

            logger.info(f"Consistency check: {problem['id']}/{sub_path.stem}")

            result1 = evaluate_single_submission(problem, sub_path, config)
            result2 = evaluate_single_submission(problem, sub_path, config)

            report = check_consistency(result1, result2)
            report["problem_id"] = problem["id"]
            report["submission_id"] = sub_path.stem
            consistency_results.append(report)

            count += 1

        if count >= sample_size:
            break

    return consistency_results


def run_grader_accuracy(
    results: list[EvaluationResult],
    gold_path: str = "dataset/gold_scores.json",
) -> dict:
    """Compare evaluation results against gold standard scores."""
    if not os.path.exists(gold_path):
        logger.warning(f"Gold scores file not found: {gold_path}")
        return {}

    with open(gold_path) as f:
        gold_data = json.load(f)

    # Build lookup
    gold_lookup = {}
    for g in gold_data:
        key = f"{g['problem_id']}/{g['submission_id']}"
        gold_lookup[key] = g

    predicted = []
    gold_list = []

    for r in results:
        key = f"{r.problem_id}/{r.submission_id}"
        if key in gold_lookup:
            g = gold_lookup[key]
            scores = r.llm_judgment.scores
            predicted.append({
                "correctness": scores.correctness,
                "edge_cases": scores.edge_cases,
                "complexity": scores.complexity,
                "style": scores.style,
                "clarity": scores.clarity,
                "overall": r.final_score,
            })
            gold_list.append({
                "correctness": g["correctness"],
                "edge_cases": g["edge_cases"],
                "complexity": g["complexity"],
                "style": g["style"],
                "clarity": g["clarity"],
                "overall": g["overall"],
            })

    if not predicted:
        logger.warning("No matching submissions found in gold scores")
        return {}

    return compute_grader_accuracy(predicted, gold_list)
