"""Static analysis using ruff (and optionally mypy)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

from evaluator.schema import StaticWarning


def run_ruff(code: str) -> list[StaticWarning]:
    """Run ruff linter on code and return warnings."""
    warnings = []

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as f:
        f.write(code)
        f.flush()
        tmp_path = f.name

    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "ruff", "check",
                "--output-format", "json",
                "--select", "E,W,F,C,N,B",
                tmp_path,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.stdout.strip():
            try:
                issues = json.loads(result.stdout)
                for issue in issues:
                    warnings.append(
                        StaticWarning(
                            rule=issue.get("code", "unknown"),
                            message=issue.get("message", ""),
                            line=issue.get("location", {}).get("row", 0),
                            column=issue.get("location", {}).get("column", 0),
                            severity="warning",
                        )
                    )
            except json.JSONDecodeError:
                pass

    except (subprocess.TimeoutExpired, FileNotFoundError):
        warnings.append(
            StaticWarning(
                rule="TOOL_ERROR",
                message="ruff not available or timed out",
                severity="info",
            )
        )
    finally:
        os.unlink(tmp_path)

    return warnings


def run_static_analysis(code: str) -> list[StaticWarning]:
    """Run all static analysis tools on code."""
    warnings = run_ruff(code)
    return warnings


def count_by_severity(warnings: list[StaticWarning]) -> dict[str, int]:
    """Count warnings by severity."""
    counts: dict[str, int] = {}
    for w in warnings:
        counts[w.severity] = counts.get(w.severity, 0) + 1
    return counts


def style_score_from_warnings(warnings: list[StaticWarning], code_lines: int) -> float:
    """
    Compute a style score from 0-10 based on static analysis warnings.

    Fewer warnings per line of code = higher score.
    """
    if code_lines == 0:
        return 5.0

    warning_count = len([w for w in warnings if w.rule != "TOOL_ERROR"])
    warning_density = warning_count / max(code_lines, 1)

    if warning_density == 0:
        return 10.0
    elif warning_density < 0.05:
        return 9.0
    elif warning_density < 0.1:
        return 8.0
    elif warning_density < 0.2:
        return 6.0
    elif warning_density < 0.3:
        return 4.0
    elif warning_density < 0.5:
        return 2.0
    else:
        return 1.0
