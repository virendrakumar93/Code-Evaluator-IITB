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


---

## Step-by-Step Setup Guide

### Prerequisites

- **Python 3.10 or higher** (check with `python3 --version`)
- **pip** (comes with Python; check with `pip --version`)
- **Internet connection** (needed for HuggingFace API calls)
- **No GPU required** — all LLM inference happens remotely via HuggingFace API

### Step 1: Clone the Repository

Open a terminal and run:

```bash
git clone https://github.com/virendrakumar93/Code-Evaluator-IITB.git

Then navigate into the project folder:

cd Code-Evaluator-IITB/Code_Evaluator-Code-Evaluator-IITB
Step 2: (Recommended) Create a Virtual Environment
This keeps the project dependencies isolated from your system Python:

# Create a virtual environment
python3 -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

You should see (venv) appear at the start of your terminal prompt.
Step 3: Install Dependencies
pip install -r requirements.txt

This installs:

pyyaml — for reading the config file
python-dotenv — for loading the .env file
requests — for making API calls to HuggingFace
ruff — for static code analysis (linting)
Step 4: Get a HuggingFace API Key
Go to https://huggingface.co/settings/tokens
Sign up or log in to your HuggingFace account
Click "New token"
Give it a name (e.g., code-evaluator), select "Read" access
Click "Generate"
Copy the token — it starts with hf_...
Step 5: Set Up the API Key
Copy the example environment file and add your key:

cp .env.example .env

Now open the .env file in any text editor:

# Using nano (Linux/macOS):
nano .env

# Or using any editor you prefer:
# code .env        (VS Code)
# vim .env         (Vim)
# notepad .env     (Windows)

Replace the placeholder with your actual key:

HF_API_KEY=hf_your_actual_key_here

Save the file and close the editor.

Note: The .env file is listed in .gitignore, so your API key will NOT be pushed to GitHub.

Step 6: Run the Evaluation Pipeline
You have two options:

Option A: Using Make (recommended, simpler)
# Full pipeline (with LLM evaluation + consistency check)
make run

Option B: Using Python directly
# Full pipeline (with LLM evaluation + consistency check)
python cli.py --evaluate all --consistency-check

Run WITHOUT LLM (no API key needed)
If you just want to test the deterministic scoring without the LLM component:

make run-no-llm
# or
python cli.py --evaluate all --no-llm

This skips the HuggingFace API calls and uses only test results + static analysis for scoring.

Step 7: View the Results
After the pipeline finishes, you'll find:

File	Description
reports/evaluation_report.md	Full evaluation report with scores, accuracy metrics, consistency checks, and hallucination audit
reports/results.json	Machine-readable JSON with all evaluation data
reports/design_note.md	System design rationale document
Open the evaluation report:

# On Linux:
cat reports/evaluation_report.md

# Or open in your editor:
code reports/evaluation_report.md

Usage Examples
Evaluate all submissions for all problems
python cli.py --evaluate all --consistency-check

Evaluate all submissions for a specific problem
python cli.py --evaluate problem_1

Evaluate a single specific submission
python cli.py --evaluate problem_1 --submission correct_optimal

Run only the consistency check
python cli.py --consistency-check --consistency-samples 10

Verbose mode (see detailed logs)
python cli.py --evaluate all -v

All Make commands
make help             # Show all available commands
make setup            # Install dependencies only
make run              # Full pipeline (LLM + consistency)
make run-no-llm       # Pipeline without LLM (no API key needed)
make consistency      # Consistency check only
make clean            # Remove generated reports
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

#Project Structure
```
Code_Evaluator-Code-Evaluator-IITB/
├── cli.py                  # Main entry point — run this
├── config.yaml             # Pipeline configuration (models, weights, timeouts)
├── requirements.txt        # Python dependencies
├── Makefile                # Shortcut commands (make run, make clean, etc.)
├── .env.example            # Template for your API key (copy to .env)
├── .gitignore              # Files excluded from git
├── evaluator/              # Core evaluation engine
│   ├── orchestrator.py     # Pipeline coordinator — ties everything together
│   ├── sandbox.py          # Safe code execution (subprocess with timeout)
│   ├── test_runner.py      # Runs unit tests against submissions
│   ├── static_analysis.py  # Ruff linter integration
│   ├── rubric_engine.py    # Deterministic scoring (test + analysis based)
│   ├── llm_judge.py        # HuggingFace LLM evaluation
│   ├── schema.py           # Data models / type definitions
│   └── consistency_checker.py  # Consistency & hallucination audit
├── problems/               # Problem sets (5 problems)
│   ├── problem_1/          # Two Sum (Arrays/Strings)
│   ├── problem_2/          # Balanced Parentheses (Recursion)
│   ├── problem_3/          # Climbing Stairs (Dynamic Programming)
│   ├── problem_4/          # Arithmetic Expression (Parsing)
│   └── problem_5/          # BFS Shortest Path (Graph)
│       ├── description.md      # Problem statement
│       ├── reference.py        # Reference solution
│       ├── tests.py            # 10 unit tests
│       └── submissions/        # Student submissions (correct, buggy, etc.)
├── dataset/
│   └── gold_scores.json    # Gold standard annotations for accuracy benchmarking
└── reports/                # Generated output (after running the pipeline)
    ├── evaluation_report.md    # Full evaluation report
    ├── results.json            # Machine-readable results
    └── design_note.md          # System design rationale
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
Troubleshooting
"HuggingFace API key not found"
Make sure you created the .env file (not just .env.example)
Make sure the key is on its own line: HF_API_KEY=hf_your_key_here
No quotes around the key value
Make sure the file is in the same directory as cli.py
"Model loading, waiting 30s..."
This is normal. HuggingFace free-tier models need to "warm up" if they haven't been used recently. The pipeline will wait and retry automatically.
"All LLM attempts failed. Using deterministic scores."
The LLM API may be temporarily unavailable. The pipeline gracefully falls back to deterministic-only scoring. Your results will still be generated.
Check your internet connection and API key validity.
Rate limit errors
HuggingFace free tier has rate limits. Wait a few minutes and try again, or use --no-llm flag to skip LLM calls entirely.
"ModuleNotFoundError: No module named '...'"
Make sure you ran pip install -r requirements.txt
If using a virtual environment, make sure it's activated (source venv/bin/activate)


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
