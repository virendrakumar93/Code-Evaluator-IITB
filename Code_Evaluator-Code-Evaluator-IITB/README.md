# Code Evaluator — Reliable Coding Evaluation Pipeline

A tool-augmented LLM pipeline for evaluating Python coding submissions with evidence-grounded grading, hallucination detection, and structured rubric-aligned scoring.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI (cli.py)                              │
├─────────────────────────────────────────────────────────────┤
│                 Orchestrator                                 │
│   ┌──────────┐  ┌─────────────┐  ┌──────────────────┐      │
│   │ Sandbox  │→ │ Test Runner │→ │ Static Analysis  │      │
│   │ (subprocess │  │ (unittest)  │  │ (ruff)           │      │
│   │  timeout)   │  │             │  │                  │      │
│   └──────────┘  └─────────────┘  └──────────────────┘      │
│         ↓              ↓                  ↓                  │
│   ┌─────────────────────────────────────────┐               │
│   │         Evidence Bundle                  │               │
│   └─────────────────────────────────────────┘               │
│         ↓                          ↓                         │
│   ┌──────────────┐    ┌──────────────────────┐              │
│   │ Rubric Engine│    │   LLM Judge          │              │
│   │ (deterministic│    │ (HuggingFace API)    │              │
│   │  scoring)     │    │ (Qwen2.5-Coder)     │              │
│   └──────────────┘    └──────────────────────┘              │
│         ↓                          ↓                         │
│   ┌─────────────────────────────────────────┐               │
│   │       Consistency Checker &              │               │
│   │       Hallucination Auditor              │               │
│   └─────────────────────────────────────────┘               │
│                        ↓                                     │
│              Final Blended Score                             │
│         (60% deterministic + 40% LLM)                       │
│                        ↓                                     │
│             Evaluation Report (.md + .json)                  │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/virendrakumar93/Code_Evaluator.git
cd Code_Evaluator

# 2. Set up environment
cp .env.example .env
# Edit .env and add your HuggingFace API key

# 3. Install dependencies and run
make run
```

Or without Make:

```bash
pip install -r requirements.txt
python cli.py --evaluate all --consistency-check
```

## Setup Instructions

### Prerequisites
- Python 3.10+
- pip

### Hardware Requirements
- **CPU only** — all LLM inference is via HuggingFace Inference API
- ~100MB disk for dependencies
- Internet connection for HuggingFace API calls

### Getting a HuggingFace API Key
1. Go to https://huggingface.co/settings/tokens
2. Create a new token (read access is sufficient)
3. Copy the token and add it to your `.env` file

### Installation
```bash
pip install -r requirements.txt
```

## Usage

### Full Pipeline
```bash
# With LLM evaluation
python cli.py --evaluate all --consistency-check

# Without LLM (deterministic scoring only — no API key needed)
python cli.py --evaluate all --no-llm

# Verbose output
python cli.py --evaluate all -v
```

### Single Problem/Submission
```bash
# All submissions for a problem
python cli.py --evaluate problem_1

# Specific submission
python cli.py --evaluate problem_1 --submission correct_optimal
```

### Consistency Check Only
```bash
python cli.py --consistency-check --consistency-samples 10
```

## Example Output

```json
{
  "problem_id": "problem_1",
  "submission_id": "correct_optimal",
  "deterministic_score": 0.9555,
  "llm_adjusted_score": 0.9400,
  "final_score": 0.9493,
  "execution_artifact": {
    "test_results": {
      "total": 10,
      "passed": 10,
      "failed": 0,
      "errors": 0,
      "pass_rate": 1.0
    },
    "static_warnings": [],
    "timeout": false,
    "sandbox_violation": false
  },
  "llm_judgment": {
    "scores": {
      "correctness": 10.0,
      "edge_cases": 10.0,
      "complexity": 10.0,
      "style": 9.0,
      "clarity": 8.5
    },
    "issues": [],
    "suggestions": ["Consider adding type hints for return value"],
    "evidence_used": ["test_pass_rate: 100%", "no_static_warnings"],
    "confidence": 0.95,
    "uncertainty_flags": []
  },
  "hallucination_flags": []
}
```

## Project Structure

```
code_evaluator/
├── problems/
│   ├── problem_1/          # Two Sum (Arrays/Strings)
│   ├── problem_2/          # Balanced Parentheses (Recursion)
│   ├── problem_3/          # Climbing Stairs (DP)
│   ├── problem_4/          # Arithmetic Expression (Parsing)
│   └── problem_5/          # BFS Shortest Path (Graph)
│       ├── description.md
│       ├── reference.py
│       ├── tests.py
│       └── submissions/
│           ├── correct_*.py
│           ├── wrong_logic.py
│           ├── edge_case_bug.py
│           ├── style_poor.py
│           └── ...
├── evaluator/
│   ├── orchestrator.py     # Pipeline coordinator
│   ├── sandbox.py          # Safe code execution
│   ├── test_runner.py      # Unit test execution
│   ├── static_analysis.py  # ruff integration
│   ├── rubric_engine.py    # Deterministic scoring
│   ├── llm_judge.py        # HuggingFace LLM evaluation
│   ├── schema.py           # Data models
│   └── consistency_checker.py  # Consistency & hallucination audit
├── dataset/
│   └── gold_scores.json    # Gold standard annotations
├── reports/
│   ├── evaluation_report.md
│   └── design_note.md
├── cli.py                  # Main entry point
├── config.yaml             # Pipeline configuration
├── requirements.txt
├── Makefile
├── .env.example
└── README.md
```

## Rubric Dimensions

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| Correctness | 35% | Test pass rate |
| Edge Cases | 20% | Handling of boundary conditions |
| Complexity | 15% | Algorithmic efficiency |
| Style | 15% | Code formatting, naming, linting |
| Clarity | 15% | Readability and structure |

## How to Extend

### Adding a New Problem
1. Create a directory under `problems/` (e.g., `problems/problem_6/`)
2. Add `description.md`, `reference.py`, and `tests.py`
3. Add submissions under `submissions/`
4. Update the function name mapping in `evaluator/orchestrator.py`
5. Add gold scores to `dataset/gold_scores.json`

### Switching the LLM
Edit `config.yaml`:
```yaml
llm:
  model: "your-model/name-here"
```

Any HuggingFace Inference API compatible model works.

## Known Limitations

1. **Sandbox:** Uses subprocess isolation, not Docker containers. Sufficient for evaluation but not for untrusted production workloads.
2. **Complexity Analysis:** AST-based loop nesting is a heuristic. It cannot detect all algorithmic complexity patterns (e.g., amortized analysis, recursive complexity).
3. **LLM Latency:** HuggingFace Inference API can be slow (5-15s per call). Models may need cold-start loading time.
4. **Free Tier Limits:** HuggingFace free tier has rate limits. For large-scale evaluation, consider a Pro subscription or local inference.
5. **Single Language:** Currently supports Python submissions only.
6. **Sequential Processing:** Submissions are evaluated sequentially. Parallel evaluation is planned.

## Reports Generated

- `reports/evaluation_report.md` — Full evaluation with scores, accuracy metrics, consistency checks, and hallucination audit
- `reports/results.json` — Machine-readable evaluation results
- `reports/design_note.md` — System design rationale

## License

MIT
