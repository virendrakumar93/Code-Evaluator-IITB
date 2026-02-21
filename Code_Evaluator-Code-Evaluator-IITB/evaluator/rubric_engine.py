"""Deterministic rubric scoring engine with partial credit."""

from __future__ import annotations

import ast
import re

from evaluator.schema import (
    ExecutionArtifact,
    RubricScores,
    StaticWarning,
    TestSuiteResult,
)
from evaluator.static_analysis import style_score_from_warnings


def compute_correctness_score(test_result: TestSuiteResult) -> float:
    """Score correctness based on test pass rate (0-10)."""
    return round(test_result.pass_rate * 10, 2)


def compute_edge_case_score(test_result: TestSuiteResult) -> float:
    """
    Score edge case handling.

    If most tests pass but some fail, likely edge case issues.
    Apply partial credit curve.
    """
    if test_result.total == 0:
        return 0.0

    pass_rate = test_result.pass_rate

    if pass_rate >= 1.0:
        return 10.0
    elif pass_rate >= 0.8:
        return 7.0 + (pass_rate - 0.8) * 15
    elif pass_rate >= 0.5:
        return 4.0 + (pass_rate - 0.5) * 10
    else:
        return pass_rate * 8


def estimate_complexity(code: str, expected_optimal: str = "O(n)") -> float:
    """
    Estimate time complexity score based on code patterns.

    Returns 0-10 score. Penalizes nested loops when O(n) expected.
    """
    score = 10.0
    nested_loop_depth = 0
    current_depth = 0

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return 3.0

    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.While)):
            current_depth += 1
            nested_loop_depth = max(nested_loop_depth, current_depth)

    # Reset - we need proper nesting analysis
    nested_loop_depth = _count_max_loop_nesting(tree)

    if "O(n)" in expected_optimal or "O(V+E)" in expected_optimal:
        if nested_loop_depth >= 3:
            score = 2.0
        elif nested_loop_depth >= 2:
            score = 5.0
        elif nested_loop_depth == 1:
            score = 9.0
        else:
            score = 10.0
    elif "O(n^2)" in expected_optimal:
        if nested_loop_depth >= 3:
            score = 4.0
        elif nested_loop_depth >= 2:
            score = 8.0
        else:
            score = 10.0

    # Check for recursion without memoization
    has_recursion = _has_recursion(code)
    has_memo = "memo" in code or "cache" in code or "lru_cache" in code or "@cache" in code
    if has_recursion and not has_memo and "O(n)" in expected_optimal:
        score = min(score, 6.0)

    return round(score, 2)


def _count_max_loop_nesting(tree: ast.AST) -> int:
    """Count maximum nesting depth of loops."""
    max_depth = 0

    def walk(node: ast.AST, depth: int = 0) -> None:
        nonlocal max_depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While)):
                new_depth = depth + 1
                max_depth = max(max_depth, new_depth)
                walk(child, new_depth)
            else:
                walk(child, depth)

    walk(tree)
    return max_depth


def _has_recursion(code: str) -> bool:
    """Check if code likely contains recursion."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False

    func_names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_names.add(node.name)

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in func_names:
                return True
    return False


def compute_style_score(
    code: str, warnings: list[StaticWarning]
) -> float:
    """Score code style based on static analysis and heuristics."""
    lines = code.strip().split("\n")
    num_lines = len(lines)

    base_score = style_score_from_warnings(warnings, num_lines)

    # Additional style heuristics
    deductions = 0.0

    # Check for single-char variable names (excluding i, j, k, n, x, y)
    acceptable_short = {"i", "j", "k", "n", "x", "y", "v", "e", "f", "s", "t", "q", "_"}
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and len(node.id) == 1:
                if node.id not in acceptable_short:
                    deductions += 0.3
    except SyntaxError:
        deductions += 2.0

    # Check for very long lines
    long_lines = sum(1 for line in lines if len(line) > 100)
    if long_lines > 0:
        deductions += min(long_lines * 0.3, 2.0)

    # Check for missing spaces around operators (crude check)
    cramped = sum(1 for line in lines if re.search(r"[a-zA-Z0-9][=<>!]+[a-zA-Z0-9]", line) and "==" not in line and "!=" not in line and ">=" not in line and "<=" not in line)
    if cramped > 2:
        deductions += 1.0

    return round(max(0.0, min(10.0, base_score - deductions)), 2)


def compute_clarity_score(code: str) -> float:
    """Score code clarity based on readability heuristics."""
    score = 8.0
    lines = code.strip().split("\n")
    num_lines = len(lines)

    # Function length penalty
    if num_lines > 50:
        score -= 2.0
    elif num_lines > 30:
        score -= 1.0

    # Check for meaningful function/variable names
    try:
        tree = ast.parse(code)
        func_count = 0
        short_func_names = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_count += 1
                if len(node.name) <= 2:
                    short_func_names += 1

        if func_count > 0 and short_func_names / func_count > 0.5:
            score -= 2.0
    except SyntaxError:
        score -= 3.0

    # Check for docstrings
    has_docstring = '"""' in code or "'''" in code
    if has_docstring:
        score += 1.0

    # Has comments (useful ones)
    comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
    if comment_lines > 0 and num_lines > 10:
        score += 0.5

    return round(max(0.0, min(10.0, score)), 2)


def compute_deterministic_scores(
    code: str,
    test_result: TestSuiteResult,
    warnings: list[StaticWarning],
    expected_complexity: str = "O(n)",
) -> RubricScores:
    """Compute all deterministic rubric scores."""
    return RubricScores(
        correctness=compute_correctness_score(test_result),
        edge_cases=compute_edge_case_score(test_result),
        complexity=estimate_complexity(code, expected_complexity),
        style=compute_style_score(code, warnings),
        clarity=compute_clarity_score(code),
    )
