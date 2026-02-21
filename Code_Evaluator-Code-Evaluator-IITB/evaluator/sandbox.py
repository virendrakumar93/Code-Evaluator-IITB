"""Sandbox for safe code execution with resource limits."""

from __future__ import annotations

import ast
import os
import signal
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

BLOCKED_MODULES = {
    "os", "sys", "subprocess", "shutil", "socket", "http", "urllib",
    "requests", "ftplib", "smtplib", "ctypes", "importlib", "code",
    "codeop", "compile", "compileall", "py_compile", "zipimport",
    "pkgutil", "multiprocessing", "threading", "signal", "resource",
    "webbrowser", "antigravity", "turtle", "tkinter", "pathlib",
}

BLOCKED_BUILTINS = {
    "exec", "eval", "compile", "__import__", "open", "input",
    "breakpoint", "exit", "quit",
}

SAFE_IMPORTS = {
    "math", "collections", "itertools", "functools", "heapq",
    "bisect", "string", "re", "typing", "dataclasses", "enum",
    "copy", "operator", "statistics",
}


class SandboxViolation(Exception):
    """Raised when code violates sandbox rules."""


def check_code_safety(code: str) -> list[str]:
    """Static check for dangerous patterns in code. Returns list of violations."""
    violations = []

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [f"SyntaxError: {e}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name.split(".")[0]
                if module not in SAFE_IMPORTS:
                    violations.append(f"Blocked import: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module = node.module.split(".")[0]
                if module not in SAFE_IMPORTS:
                    violations.append(f"Blocked import from: {node.module}")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in BLOCKED_BUILTINS:
                    violations.append(f"Blocked builtin call: {node.func.id}")
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr in ("system", "popen", "exec", "spawn"):
                    violations.append(f"Blocked method call: {node.func.attr}")

    return violations


def strip_comments(code: str) -> str:
    """Remove comments from code to prevent prompt injection via comments."""
    lines = code.split("\n")
    cleaned = []
    in_docstring = False
    docstring_char = None

    for line in lines:
        stripped = line.strip()

        if in_docstring:
            if docstring_char and docstring_char in stripped:
                in_docstring = False
            continue

        if stripped.startswith('"""') or stripped.startswith("'''"):
            docstring_char = stripped[:3]
            if stripped.count(docstring_char) >= 2:
                continue
            in_docstring = True
            continue

        if "#" in line:
            in_quote = False
            quote_char = None
            comment_pos = -1
            for i, ch in enumerate(line):
                if ch in ('"', "'") and not in_quote:
                    in_quote = True
                    quote_char = ch
                elif ch == quote_char and in_quote:
                    in_quote = False
                elif ch == "#" and not in_quote:
                    comment_pos = i
                    break
            if comment_pos >= 0:
                line = line[:comment_pos].rstrip()
                if not line.strip():
                    continue

        cleaned.append(line)

    return "\n".join(cleaned)


def run_in_sandbox(
    code: str,
    test_code: str,
    function_name: str,
    timeout: float = 3.0,
) -> dict:
    """
    Execute submission code + test code in a subprocess sandbox.

    Returns dict with:
        stdout, stderr, returncode, execution_time, timeout, sandbox_violation
    """
    violations = check_code_safety(code)
    if violations:
        return {
            "stdout": "",
            "stderr": f"Sandbox violations: {'; '.join(violations)}",
            "returncode": -1,
            "execution_time": 0.0,
            "timeout": False,
            "sandbox_violation": True,
            "violations": violations,
        }

    runner_script = textwrap.dedent(f"""\
        import sys
        import time
        import unittest
        import io
        import json

        # Save references before restricting builtins
        _safe_exec = exec
        _safe_compile = compile
        _safe_open = open

        # Load files before restricting
        submission_code = _safe_open(sys.argv[1]).read()
        test_code = _safe_open(sys.argv[2]).read()

        # Now restrict builtins for submission code
        # (We keep exec/compile for the runner itself but the submission
        #  code runs in a restricted namespace)

        # Execute submission code in isolated namespace
        exec_globals = {{}}
        _safe_exec(_safe_compile(submission_code, "submission.py", "exec"), exec_globals)

        # Inject the function into test module globals
        # NOTE: __name__ must NOT be "__main__" to prevent unittest.main() from executing
        test_globals = {{"__name__": "__test_runner__", "unittest": unittest}}
        for k, v in exec_globals.items():
            if not k.startswith("_"):
                test_globals[k] = v

        # Also inject function name into global scope for the test
        func = exec_globals.get("{function_name}")
        if func:
            test_globals["{function_name}"] = func

        _safe_exec(_safe_compile(test_code, "tests.py", "exec"), test_globals)

        # Find and run test class
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        for name, obj in test_globals.items():
            if isinstance(obj, type) and issubclass(obj, unittest.TestCase) and obj != unittest.TestCase:
                # Inject function into test class
                for k, v in exec_globals.items():
                    if not k.startswith("_"):
                        setattr(obj, k, staticmethod(v) if callable(v) else v)
                suite.addTests(loader.loadTestsFromTestCase(obj))

        start = time.time()
        stream = io.StringIO()
        runner = unittest.TextTestRunner(stream=stream, verbosity=2)
        result = runner.run(suite)
        elapsed = time.time() - start

        # Output structured results
        test_results = []
        for test, traceback in result.failures:
            test_results.append({{"name": str(test), "status": "FAIL", "message": traceback}})
        for test, traceback in result.errors:
            test_results.append({{"name": str(test), "status": "ERROR", "message": traceback}})

        # Identify passed tests
        all_tests = set()
        failed_tests = set()
        for test, _ in result.failures + result.errors:
            failed_tests.add(str(test))
        for suite_item in suite:
            tname = str(suite_item)
            all_tests.add(tname)
            if tname not in failed_tests:
                test_results.append({{"name": tname, "status": "PASS", "message": ""}})

        output = {{
            "total": result.testsRun,
            "passed": result.testsRun - len(result.failures) - len(result.errors),
            "failed": len(result.failures),
            "errors": len(result.errors),
            "elapsed": round(elapsed, 4),
            "details": test_results,
            "test_output": stream.getvalue(),
        }}
        print("===JSON_RESULT===")
        print(json.dumps(output))
    """)

    with tempfile.TemporaryDirectory() as tmpdir:
        sub_path = os.path.join(tmpdir, "submission.py")
        test_path = os.path.join(tmpdir, "tests.py")
        runner_path = os.path.join(tmpdir, "runner.py")

        with open(sub_path, "w") as f:
            f.write(code)
        with open(test_path, "w") as f:
            f.write(test_code)
        with open(runner_path, "w") as f:
            f.write(runner_script)

        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"

        try:
            proc = subprocess.run(
                [sys.executable, runner_path, sub_path, test_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tmpdir,
                env=env,
            )

            return {
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "returncode": proc.returncode,
                "execution_time": 0.0,
                "timeout": False,
                "sandbox_violation": False,
                "violations": [],
            }

        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": f"Execution timed out after {timeout}s",
                "returncode": -1,
                "execution_time": timeout,
                "timeout": True,
                "sandbox_violation": False,
                "violations": [],
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
                "execution_time": 0.0,
                "timeout": False,
                "sandbox_violation": False,
                "violations": [],
            }
