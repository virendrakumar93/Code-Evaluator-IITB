#!/usr/bin/env python3
"""CLI entry point for the Code Evaluation Pipeline."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from evaluator.orchestrator import (
    evaluate_all,
    evaluate_single_submission,
    discover_problems,
    load_config,
    run_consistency_check,
    run_grader_accuracy,
)
from evaluator.schema import EvaluationResult

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("cli")


def generate_evaluation_report(
    results: list[EvaluationResult],
    accuracy_metrics: dict,
    consistency_results: list[dict],
    output_path: str = "reports/evaluation_report.md",
) -> None:
    """Generate the markdown evaluation report."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    lines = []
    lines.append("# Evaluation Report")
    lines.append("")
    lines.append(f"**Total submissions evaluated:** {len(results)}")
    lines.append("")

    # Summary table
    lines.append("## Summary")
    lines.append("")
    lines.append("| Problem | Submission | Correctness | Edge Cases | Complexity | Style | Clarity | Final Score |")
    lines.append("|---------|-----------|-------------|------------|------------|-------|---------|-------------|")

    for r in results:
        s = r.llm_judgment.scores
        lines.append(
            f"| {r.problem_id} | {r.submission_id} | "
            f"{s.correctness:.1f} | {s.edge_cases:.1f} | {s.complexity:.1f} | "
            f"{s.style:.1f} | {s.clarity:.1f} | {r.final_score:.4f} |"
        )

    lines.append("")

    # Grader Accuracy
    lines.append("## Grader Accuracy (vs Gold Standard)")
    lines.append("")

    if accuracy_metrics:
        lines.append("| Dimension | MAE | Exact Match % | Correlation | N |")
        lines.append("|-----------|-----|---------------|-------------|---|")
        for dim, m in accuracy_metrics.items():
            lines.append(
                f"| {dim} | {m['mae']:.4f} | {m['exact_match_pct']:.1f}% | "
                f"{m['correlation']:.4f} | {m['n']} |"
            )
    else:
        lines.append("*Gold scores not available or no matching submissions.*")

    lines.append("")

    # Consistency Check
    lines.append("## Consistency Check")
    lines.append("")

    if consistency_results:
        all_consistent = all(c["consistent"] for c in consistency_results)
        lines.append(
            f"**Overall consistency:** {'PASS' if all_consistent else 'FAIL'}"
        )
        lines.append("")

        for c in consistency_results:
            status = "CONSISTENT" if c["consistent"] else "INCONSISTENT"
            lines.append(
                f"- {c['problem_id']}/{c['submission_id']}: **{status}** "
                f"(det_diff={c['deterministic_diff']:.4f}, "
                f"final_diff={c['final_score_diff']:.4f})"
            )
    else:
        lines.append("*Consistency check not run.*")

    lines.append("")

    # Hallucination Audit
    lines.append("## Hallucination Audit")
    lines.append("")

    total_flags = 0
    for r in results:
        if r.hallucination_flags:
            total_flags += len(r.hallucination_flags)
            lines.append(f"### {r.problem_id}/{r.submission_id}")
            for flag in r.hallucination_flags:
                lines.append(f"- {flag}")
            lines.append("")

    if total_flags == 0:
        lines.append("**No hallucination flags detected.**")
    else:
        lines.append(f"**Total hallucination flags:** {total_flags}")

    lines.append("")

    # Detailed results per problem
    lines.append("## Detailed Results")
    lines.append("")

    current_problem = None
    for r in results:
        if r.problem_id != current_problem:
            current_problem = r.problem_id
            lines.append(f"### {current_problem}")
            lines.append("")

        lines.append(f"#### {r.submission_id}")
        lines.append("")
        lines.append(f"- **Final Score:** {r.final_score:.4f}")
        lines.append(f"- **Deterministic Score:** {r.deterministic_score:.4f}")
        lines.append(f"- **LLM Adjusted Score:** {r.llm_adjusted_score:.4f}")
        lines.append(f"- **Test Pass Rate:** {r.execution_artifact.test_results.pass_rate:.0%}")
        lines.append(f"- **Tests:** {r.execution_artifact.test_results.passed}/{r.execution_artifact.test_results.total} passed")
        lines.append(f"- **Static Warnings:** {len(r.execution_artifact.static_warnings)}")
        lines.append(f"- **Timeout:** {r.execution_artifact.timeout}")
        lines.append(f"- **Sandbox Violation:** {r.execution_artifact.sandbox_violation}")

        if r.llm_judgment.issues:
            lines.append(f"- **Issues:** {'; '.join(r.llm_judgment.issues[:3])}")

        if r.llm_judgment.suggestions:
            lines.append(f"- **Suggestions:** {'; '.join(r.llm_judgment.suggestions[:3])}")

        lines.append("")

    report_text = "\n".join(lines)

    with open(output_path, "w") as f:
        f.write(report_text)

    logger.info(f"Evaluation report saved to {output_path}")


def save_results_json(
    results: list[EvaluationResult],
    output_path: str = "reports/results.json",
) -> None:
    """Save raw results as JSON."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    data = [r.to_dict() for r in results]
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info(f"Results JSON saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Code Evaluation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py --evaluate all
  python cli.py --evaluate all --no-llm
  python cli.py --evaluate problem_1 --submission correct_optimal
  python cli.py --consistency-check
  python cli.py --evaluate all --consistency-check
        """,
    )

    parser.add_argument(
        "--evaluate",
        type=str,
        help="Evaluate submissions: 'all' or a specific problem_id",
    )
    parser.add_argument(
        "--submission",
        type=str,
        help="Specific submission to evaluate (used with --evaluate <problem_id>)",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to config file (default: config.yaml)",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM evaluation (use deterministic scores only)",
    )
    parser.add_argument(
        "--consistency-check",
        action="store_true",
        help="Run consistency check on a sample",
    )
    parser.add_argument(
        "--consistency-samples",
        type=int,
        default=5,
        help="Number of samples for consistency check (default: 5)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="reports",
        help="Output directory for reports (default: reports)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load config
    config = load_config(args.config)

    if args.no_llm:
        config.setdefault("llm", {})["enabled"] = False

    results = []
    consistency_results = []
    accuracy_metrics = {}

    if args.evaluate:
        if args.evaluate == "all":
            logger.info("=" * 60)
            logger.info("STARTING FULL EVALUATION PIPELINE")
            logger.info("=" * 60)

            results = evaluate_all(config)

            logger.info(f"\nEvaluated {len(results)} submissions")

            # Grader accuracy
            gold_path = config.get("paths", {}).get(
                "gold_scores", "dataset/gold_scores.json"
            )
            accuracy_metrics = run_grader_accuracy(results, gold_path)

        else:
            # Evaluate specific problem
            problems = discover_problems(
                config.get("paths", {}).get("problems", "problems")
            )
            target = [p for p in problems if p["id"] == args.evaluate]

            if not target:
                logger.error(f"Problem '{args.evaluate}' not found")
                sys.exit(1)

            problem = target[0]

            if args.submission:
                # Single submission
                sub_files = [
                    s for s in problem["submissions"]
                    if s.stem == args.submission
                ]
                if not sub_files:
                    logger.error(
                        f"Submission '{args.submission}' not found "
                        f"for {args.evaluate}"
                    )
                    sys.exit(1)

                result = evaluate_single_submission(
                    problem, sub_files[0], config
                )
                results = [result]

                # Print detailed result
                print(json.dumps(result.to_dict(), indent=2))
            else:
                # All submissions for one problem
                for sub_path in problem["submissions"]:
                    result = evaluate_single_submission(
                        problem, sub_path, config
                    )
                    results.append(result)

    if args.consistency_check:
        logger.info("\n" + "=" * 60)
        logger.info("RUNNING CONSISTENCY CHECK")
        logger.info("=" * 60)

        consistency_results = run_consistency_check(
            config, args.consistency_samples
        )

    if results:
        # Generate reports
        os.makedirs(args.output_dir, exist_ok=True)

        report_path = os.path.join(args.output_dir, "evaluation_report.md")
        json_path = os.path.join(args.output_dir, "results.json")

        generate_evaluation_report(
            results, accuracy_metrics, consistency_results, report_path
        )
        save_results_json(results, json_path)

        # Print summary
        print("\n" + "=" * 60)
        print("EVALUATION COMPLETE")
        print("=" * 60)
        print(f"Submissions evaluated: {len(results)}")
        print(f"Report: {report_path}")
        print(f"Results JSON: {json_path}")

        if accuracy_metrics:
            print("\nGrader Accuracy Summary:")
            for dim, m in accuracy_metrics.items():
                print(
                    f"  {dim}: MAE={m['mae']:.3f}, "
                    f"Match={m['exact_match_pct']:.0f}%, "
                    f"Corr={m['correlation']:.3f}"
                )

        if consistency_results:
            n_consistent = sum(
                1 for c in consistency_results if c["consistent"]
            )
            print(
                f"\nConsistency: {n_consistent}/{len(consistency_results)} "
                f"submissions consistent"
            )

        # Print sample output
        if results:
            print("\nSample Output (first result):")
            print(json.dumps(results[0].to_dict(), indent=2)[:2000])

    elif not args.consistency_check:
        parser.print_help()


if __name__ == "__main__":
    main()
