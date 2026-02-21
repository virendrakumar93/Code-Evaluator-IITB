"""Test runner that parses sandbox results into structured TestSuiteResult."""

from __future__ import annotations

import json
import re

from evaluator.schema import TestResult, TestSuiteResult
from evaluator.sandbox import run_in_sandbox


def extract_json_result(stdout: str) -> dict | None:
    """Extract JSON result from sandbox output."""
    marker = "===JSON_RESULT==="
    if marker in stdout:
        json_str = stdout.split(marker, 1)[1].strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
    return None


def run_tests(
    submission_code: str,
    test_code: str,
    function_name: str,
    timeout: float = 3.0,
) -> tuple[TestSuiteResult, dict]:
    """
    Run submission against tests in sandbox.

    Returns (TestSuiteResult, raw_sandbox_output).
    """
    raw = run_in_sandbox(submission_code, test_code, function_name, timeout)

    result = TestSuiteResult()

    if raw["timeout"]:
        result.total = 1
        result.failed = 1
        result.results = [
            TestResult(
                test_name="execution",
                passed=False,
                message=f"Timeout after {timeout}s",
            )
        ]
        result.compute_pass_rate()
        return result, raw

    if raw["sandbox_violation"]:
        result.total = 1
        result.errors = 1
        result.results = [
            TestResult(
                test_name="sandbox_check",
                passed=False,
                message=f"Sandbox violation: {raw.get('violations', [])}",
            )
        ]
        result.compute_pass_rate()
        return result, raw

    parsed = extract_json_result(raw["stdout"])

    if parsed is None:
        result.total = 1
        result.errors = 1
        stderr_msg = raw["stderr"][:500] if raw["stderr"] else "Unknown error"
        result.results = [
            TestResult(
                test_name="execution",
                passed=False,
                message=f"Failed to parse results. stderr: {stderr_msg}",
            )
        ]
        result.compute_pass_rate()
        return result, raw

    result.total = parsed.get("total", 0)
    result.passed = parsed.get("passed", 0)
    result.failed = parsed.get("failed", 0)
    result.errors = parsed.get("errors", 0)

    for detail in parsed.get("details", []):
        result.results.append(
            TestResult(
                test_name=detail.get("name", "unknown"),
                passed=detail.get("status") == "PASS",
                message=detail.get("message", ""),
                execution_time=parsed.get("elapsed", 0.0),
            )
        )

    result.compute_pass_rate()
    return result, raw
