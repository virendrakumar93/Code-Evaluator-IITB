"""Structured data models for the evaluation pipeline."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class TestResult:
    test_name: str
    passed: bool
    message: str = ""
    execution_time: float = 0.0


@dataclass
class TestSuiteResult:
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    results: list[TestResult] = field(default_factory=list)
    pass_rate: float = 0.0

    def compute_pass_rate(self) -> None:
        if self.total > 0:
            self.pass_rate = round(self.passed / self.total, 4)


@dataclass
class StaticWarning:
    rule: str
    message: str
    line: int = 0
    column: int = 0
    severity: str = "warning"


@dataclass
class ExecutionArtifact:
    test_results: TestSuiteResult = field(default_factory=TestSuiteResult)
    static_warnings: list[StaticWarning] = field(default_factory=list)
    runtime_errors: str = ""
    execution_time: float = 0.0
    sandbox_violation: bool = False
    timeout: bool = False


@dataclass
class RubricScores:
    correctness: float = 0.0
    edge_cases: float = 0.0
    complexity: float = 0.0
    style: float = 0.0
    clarity: float = 0.0

    def overall(self) -> float:
        weights = {
            "correctness": 0.35,
            "edge_cases": 0.20,
            "complexity": 0.15,
            "style": 0.15,
            "clarity": 0.15,
        }
        return round(
            self.correctness * weights["correctness"]
            + self.edge_cases * weights["edge_cases"]
            + self.complexity * weights["complexity"]
            + self.style * weights["style"]
            + self.clarity * weights["clarity"],
            4,
        )


@dataclass
class LLMJudgment:
    scores: RubricScores = field(default_factory=RubricScores)
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    evidence_used: list[str] = field(default_factory=list)
    confidence: float = 0.0
    uncertainty_flags: list[str] = field(default_factory=list)
    raw_response: str = ""


@dataclass
class EvaluationResult:
    problem_id: str = ""
    submission_id: str = ""
    deterministic_score: float = 0.0
    llm_adjusted_score: float = 0.0
    final_score: float = 0.0
    execution_artifact: ExecutionArtifact = field(default_factory=ExecutionArtifact)
    llm_judgment: LLMJudgment = field(default_factory=LLMJudgment)
    hallucination_flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


@dataclass
class GoldScore:
    problem_id: str
    submission_id: str
    correctness: float
    edge_cases: float
    complexity: float
    style: float
    clarity: float
    overall: float

    def to_rubric_scores(self) -> RubricScores:
        return RubricScores(
            correctness=self.correctness,
            edge_cases=self.edge_cases,
            complexity=self.complexity,
            style=self.style,
            clarity=self.clarity,
        )
