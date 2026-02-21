# Design Note: Reliable Coding Evaluation Pipeline

## 1. Model Selection & Reasoning

**Primary Model:** Qwen2.5-Coder-7B-Instruct (via HuggingFace InferenceClient)

**Why this model:**
- Purpose-built for code understanding and analysis
- Strong performance on code benchmarks (HumanEval, MBPP)
- Available via HuggingFace Inference API (no local GPU required)
- Supports structured JSON output with low temperature
- 7B parameters provide good reasoning capacity for rubric evaluation while maintaining availability

**Fallback Models:** Qwen2.5-Coder-1.5B-Instruct, StarCoder2-15B

The fallback chain ensures the pipeline degrades gracefully if the primary model is unavailable. If all models fail, the system falls back to deterministic-only scoring, ensuring the pipeline always produces results.

## 2. Prompt Design Strategy

The LLM prompt follows an **evidence-grounded evaluation** pattern:

1. **Structured Evidence Injection:** The prompt includes pre-computed test results, static analysis warnings, and deterministic scores as factual evidence the LLM must reference.

2. **Explicit Constraints:** The prompt contains explicit rules:
   - "Do NOT claim correctness if tests fail"
   - "If evidence is missing, say insufficient evidence"
   - "Flag any uncertainty explicitly"

3. **Bounded Adjustment:** LLM scores are expected to stay within +/- 2 points of deterministic baselines, with deviations requiring justification.

4. **Strict JSON Schema:** The LLM must respond in a rigid JSON format. Malformed responses trigger a retry, then fallback to deterministic scores.

5. **Comment Stripping:** Submission code is sanitized (comments removed) before LLM ingestion to prevent prompt injection attacks via code comments.

## 3. Evidence-Grounding Enforcement

The pipeline enforces evidence grounding at multiple levels:

- **Test-Based:** Correctness and edge case scores are primarily derived from actual test pass/fail rates, not LLM opinion.
- **Static Analysis-Based:** Style scores incorporate ruff linter output as ground truth.
- **Complexity Analysis:** AST-based loop nesting analysis provides objective complexity evidence.
- **Hallucination Audit:** Post-judgment, the system cross-references LLM claims against test results and static analysis. Flags are raised for:
  - High correctness claims + low test pass rate
  - High style claims + many linter warnings
  - High confidence + sparse evidence references
  - Correctness claims despite timeout/sandbox violations

## 4. Architecture: How It Reduces Hallucinations

```
Submission → Sandbox → Test Runner → Static Analysis → Deterministic Scores
                                                             ↓
                                          Evidence Bundle → LLM Judge → Scores
                                                             ↓
                                                    Hallucination Auditor
                                                             ↓
                                                      Final Score (blended)
```

The key insight: **the LLM never evaluates code in isolation.** It receives pre-computed evidence and its role is to provide nuanced reasoning adjustments, not primary scoring. The 60/40 deterministic/LLM blend ensures that even a hallucinating LLM cannot drastically distort final scores.

## 5. Failure Modes & Mitigations

| Failure Mode | Mitigation |
|-------------|------------|
| LLM returns malformed JSON | Retry once, then fallback to deterministic |
| LLM API unavailable | Full fallback to deterministic scoring |
| Submission infinite loops | 3-second timeout in subprocess sandbox |
| Malicious code (os.system, etc.) | AST-based import/builtin blocking |
| Prompt injection via comments | Comments stripped before LLM ingestion |
| Non-deterministic submissions | Tests run in isolated subprocess |
| LLM hallucination | Post-hoc hallucination audit flags discrepancies |
| Model loading delay (503) | 30-second wait + retry |

## 6. Scaling Strategy

**Current (prototype):** Sequential evaluation, single-process.

**Near-term scaling:**
- Parallel evaluation using `concurrent.futures.ProcessPoolExecutor`
- LLM response caching (keyed on submission hash + evidence hash)
- Batch HuggingFace API calls where supported

**Production scaling:**
- Docker-based sandboxing (one container per submission) for true isolation
- Queue-based architecture (Redis/Celery) for distributed evaluation
- Dedicated GPU inference (vLLM or TGI) for faster LLM responses
- Database-backed result storage for audit trail

## 7. GPU vs CPU Tradeoffs

| Aspect | CPU (Current) | GPU (Production) |
|--------|--------------|-----------------|
| LLM Inference | HuggingFace API (remote) | Local vLLM/TGI |
| Latency | ~5-15s per evaluation | ~1-3s per evaluation |
| Cost | API calls (free tier available) | GPU hardware/cloud cost |
| Reliability | Dependent on HF uptime | Self-hosted, fully controlled |
| Setup | Zero hardware requirements | Requires CUDA-capable GPU |

The current design uses the HuggingFace Inference API, making it **CPU-only locally**. All compute-heavy LLM work is offloaded to HuggingFace's infrastructure. The test execution and static analysis are lightweight and run on CPU.

For production, switching to local inference with a quantized model (e.g., Qwen2.5-Coder-7B-Q4) on a single GPU would eliminate API dependency and reduce latency by 5-10x.

## 8. Deterministic vs LLM Scoring Separation

The system maintains a clear separation:

- **Deterministic Score:** Computed from test results + static analysis + AST complexity analysis. Fully reproducible.
- **LLM-Adjusted Score:** Incorporates LLM reasoning about code quality, approach correctness, and nuanced issues.
- **Final Score:** Weighted blend (60% deterministic, 40% LLM), with LLM weight reduced to 0% if hallucination flags are present.

This separation ensures auditability: any evaluation can be explained by pointing to specific test results and static analysis evidence, even if the LLM component is removed entirely.
