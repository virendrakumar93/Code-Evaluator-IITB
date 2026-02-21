# Evaluation Report

**Total submissions evaluated:** 36

## Summary

| Problem | Submission | Correctness | Edge Cases | Complexity | Style | Clarity | Final Score |
|---------|-----------|-------------|------------|------------|-------|---------|-------------|
| problem_1 | brute_force | 10.0 | 10.0 | 5.0 | 10.0 | 8.0 | 8.9500 |
| problem_1 | correct_alt | 10.0 | 10.0 | 9.0 | 10.0 | 8.0 | 9.5500 |
| problem_1 | correct_optimal | 10.0 | 10.0 | 9.0 | 10.0 | 8.0 | 9.5500 |
| problem_1 | edge_case_bug | 8.0 | 7.0 | 5.0 | 10.0 | 8.0 | 7.6500 |
| problem_1 | partial_correct | 7.0 | 6.0 | 9.0 | 10.0 | 8.0 | 7.7000 |
| problem_1 | style_poor | 10.0 | 10.0 | 9.0 | 4.8 | 8.0 | 8.7700 |
| problem_1 | timeout_risk | 0.0 | 0.0 | 2.0 | 6.0 | 8.0 | 2.4000 |
| problem_1 | wrong_logic | 0.0 | 0.0 | 9.0 | 10.0 | 8.0 | 4.0500 |
| problem_2 | correct_iterative | 10.0 | 10.0 | 10.0 | 8.8 | 8.5 | 9.5950 |
| problem_2 | correct_recursive | 10.0 | 10.0 | 10.0 | 10.0 | 8.0 | 9.7000 |
| problem_2 | edge_case_bug | 9.0 | 8.5 | 10.0 | 10.0 | 8.5 | 9.1250 |
| problem_2 | inefficient | 10.0 | 10.0 | 10.0 | 10.0 | 8.5 | 9.7750 |
| problem_2 | missing_cases | 7.0 | 6.0 | 10.0 | 10.0 | 8.5 | 7.9250 |
| problem_2 | style_poor | 10.0 | 10.0 | 10.0 | 0.0 | 8.0 | 8.2000 |
| problem_2 | wrong_logic | 4.0 | 3.2 | 10.0 | 10.0 | 8.5 | 6.3150 |
| problem_3 | correct_dp | 10.0 | 10.0 | 9.0 | 8.0 | 8.0 | 9.2500 |
| problem_3 | correct_recursive_memo | 10.0 | 10.0 | 10.0 | 10.0 | 8.0 | 9.7000 |
| problem_3 | edge_case_bug | 7.0 | 6.0 | 9.0 | 7.0 | 8.5 | 7.3250 |
| problem_3 | naive_recursive | 0.0 | 0.0 | 6.0 | 10.0 | 8.0 | 3.6000 |
| problem_3 | partial_correct | 9.0 | 8.5 | 9.0 | 5.6 | 8.5 | 8.3150 |
| problem_3 | style_poor | 10.0 | 10.0 | 9.0 | 0.7 | 8.0 | 8.1550 |
| problem_3 | wrong_logic | 3.0 | 2.4 | 9.0 | 8.0 | 8.5 | 5.3550 |
| problem_4 | correct_recursive | 10.0 | 10.0 | 6.0 | 9.0 | 6.0 | 8.6500 |
| problem_4 | correct_stack | 10.0 | 10.0 | 5.0 | 9.0 | 7.5 | 8.7250 |
| problem_4 | edge_case_bug | 9.0 | 8.5 | 6.0 | 9.0 | 6.5 | 8.0750 |
| problem_4 | no_parens | 9.0 | 8.5 | 9.0 | 10.0 | 7.5 | 8.8250 |
| problem_4 | partial_correct | 6.0 | 5.0 | 5.0 | 9.0 | 6.5 | 6.1750 |
| problem_4 | style_poor | 10.0 | 10.0 | 6.0 | 0.0 | 5.0 | 7.1500 |
| problem_4 | wrong_precedence | 7.0 | 6.0 | 5.0 | 9.0 | 6.5 | 6.7250 |
| problem_5 | correct_alt | 10.0 | 10.0 | 5.0 | 10.0 | 8.0 | 8.9500 |
| problem_5 | correct_bfs | 10.0 | 10.0 | 5.0 | 10.0 | 8.0 | 8.9500 |
| problem_5 | edge_case_bug | 8.0 | 7.0 | 5.0 | 10.0 | 8.0 | 7.6500 |
| problem_5 | no_visited | 0.0 | 0.0 | 5.0 | 10.0 | 8.0 | 3.4500 |
| problem_5 | partial_correct | 9.0 | 8.5 | 5.0 | 10.0 | 8.0 | 8.3000 |
| problem_5 | style_poor | 10.0 | 10.0 | 5.0 | 2.1 | 8.0 | 7.7650 |
| problem_5 | wrong_logic | 9.0 | 8.5 | 9.0 | 10.0 | 8.0 | 8.9000 |

## Grader Accuracy (vs Gold Standard)

| Dimension | MAE | Exact Match % | Correlation | N |
|-----------|-----|---------------|-------------|---|
| correctness | 1.3056 | 47.2% | 0.7865 | 36 |
| edge_cases | 1.8222 | 44.4% | 0.7739 | 36 |
| complexity | 2.1389 | 16.7% | 0.2394 | 36 |
| style | 2.0944 | 11.1% | 0.8460 | 36 |
| clarity | 1.7083 | 30.6% | 0.0909 | 36 |
| overall | 1.1943 | 33.3% | 0.7537 | 36 |

## Consistency Check

**Overall consistency:** PASS

- problem_1/brute_force: **CONSISTENT** (det_diff=0.0000, final_diff=0.0000)
- problem_1/correct_alt: **CONSISTENT** (det_diff=0.0000, final_diff=0.0000)
- problem_1/correct_optimal: **CONSISTENT** (det_diff=0.0000, final_diff=0.0000)
- problem_1/edge_case_bug: **CONSISTENT** (det_diff=0.0000, final_diff=0.0000)
- problem_1/partial_correct: **CONSISTENT** (det_diff=0.0000, final_diff=0.0000)

## Hallucination Audit

**No hallucination flags detected.**

## Detailed Results

### problem_1

#### brute_force

- **Final Score:** 8.9500
- **Deterministic Score:** 8.9500
- **LLM Adjusted Score:** 8.9500
- **Test Pass Rate:** 100%
- **Tests:** 10/10 passed
- **Static Warnings:** 0
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### correct_alt

- **Final Score:** 9.5500
- **Deterministic Score:** 9.5500
- **LLM Adjusted Score:** 9.5500
- **Test Pass Rate:** 100%
- **Tests:** 10/10 passed
- **Static Warnings:** 0
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### correct_optimal

- **Final Score:** 9.5500
- **Deterministic Score:** 9.5500
- **LLM Adjusted Score:** 9.5500
- **Test Pass Rate:** 100%
- **Tests:** 10/10 passed
- **Static Warnings:** 0
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### edge_case_bug

- **Final Score:** 7.6500
- **Deterministic Score:** 7.6500
- **LLM Adjusted Score:** 7.6500
- **Test Pass Rate:** 80%
- **Tests:** 8/10 passed
- **Static Warnings:** 0
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### partial_correct

- **Final Score:** 7.7000
- **Deterministic Score:** 7.7000
- **LLM Adjusted Score:** 7.7000
- **Test Pass Rate:** 70%
- **Tests:** 7/10 passed
- **Static Warnings:** 0
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### style_poor

- **Final Score:** 8.7700
- **Deterministic Score:** 8.7700
- **LLM Adjusted Score:** 8.7700
- **Test Pass Rate:** 100%
- **Tests:** 10/10 passed
- **Static Warnings:** 1
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### timeout_risk

- **Final Score:** 2.4000
- **Deterministic Score:** 2.4000
- **LLM Adjusted Score:** 2.4000
- **Test Pass Rate:** 0%
- **Tests:** 0/1 passed
- **Static Warnings:** 2
- **Timeout:** True
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### wrong_logic

- **Final Score:** 4.0500
- **Deterministic Score:** 4.0500
- **LLM Adjusted Score:** 4.0500
- **Test Pass Rate:** 0%
- **Tests:** 0/10 passed
- **Static Warnings:** 0
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

### problem_2

#### correct_iterative

- **Final Score:** 9.5950
- **Deterministic Score:** 9.5950
- **LLM Adjusted Score:** 9.5950
- **Test Pass Rate:** 100%
- **Tests:** 10/10 passed
- **Static Warnings:** 0
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### correct_recursive

- **Final Score:** 9.7000
- **Deterministic Score:** 9.7000
- **LLM Adjusted Score:** 9.7000
- **Test Pass Rate:** 100%
- **Tests:** 10/10 passed
- **Static Warnings:** 0
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### edge_case_bug

- **Final Score:** 9.1250
- **Deterministic Score:** 9.1250
- **LLM Adjusted Score:** 9.1250
- **Test Pass Rate:** 90%
- **Tests:** 9/10 passed
- **Static Warnings:** 0
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### inefficient

- **Final Score:** 9.7750
- **Deterministic Score:** 9.7750
- **LLM Adjusted Score:** 9.7750
- **Test Pass Rate:** 100%
- **Tests:** 10/10 passed
- **Static Warnings:** 0
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### missing_cases

- **Final Score:** 7.9250
- **Deterministic Score:** 7.9250
- **LLM Adjusted Score:** 7.9250
- **Test Pass Rate:** 70%
- **Tests:** 7/10 passed
- **Static Warnings:** 0
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### style_poor

- **Final Score:** 8.2000
- **Deterministic Score:** 8.2000
- **LLM Adjusted Score:** 8.2000
- **Test Pass Rate:** 100%
- **Tests:** 10/10 passed
- **Static Warnings:** 5
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### wrong_logic

- **Final Score:** 6.3150
- **Deterministic Score:** 6.3150
- **LLM Adjusted Score:** 6.3150
- **Test Pass Rate:** 40%
- **Tests:** 4/10 passed
- **Static Warnings:** 0
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

### problem_3

#### correct_dp

- **Final Score:** 9.2500
- **Deterministic Score:** 9.2500
- **LLM Adjusted Score:** 9.2500
- **Test Pass Rate:** 100%
- **Tests:** 10/10 passed
- **Static Warnings:** 1
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### correct_recursive_memo

- **Final Score:** 9.7000
- **Deterministic Score:** 9.7000
- **LLM Adjusted Score:** 9.7000
- **Test Pass Rate:** 100%
- **Tests:** 10/10 passed
- **Static Warnings:** 0
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### edge_case_bug

- **Final Score:** 7.3250
- **Deterministic Score:** 7.3250
- **LLM Adjusted Score:** 7.3250
- **Test Pass Rate:** 70%
- **Tests:** 7/10 passed
- **Static Warnings:** 1
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### naive_recursive

- **Final Score:** 3.6000
- **Deterministic Score:** 3.6000
- **LLM Adjusted Score:** 3.6000
- **Test Pass Rate:** 0%
- **Tests:** 0/1 passed
- **Static Warnings:** 0
- **Timeout:** True
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### partial_correct

- **Final Score:** 8.3150
- **Deterministic Score:** 8.3150
- **LLM Adjusted Score:** 8.3150
- **Test Pass Rate:** 90%
- **Tests:** 9/10 passed
- **Static Warnings:** 1
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### style_poor

- **Final Score:** 8.1550
- **Deterministic Score:** 8.1550
- **LLM Adjusted Score:** 8.1550
- **Test Pass Rate:** 100%
- **Tests:** 10/10 passed
- **Static Warnings:** 5
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### wrong_logic

- **Final Score:** 5.3550
- **Deterministic Score:** 5.3550
- **LLM Adjusted Score:** 5.3550
- **Test Pass Rate:** 30%
- **Tests:** 3/10 passed
- **Static Warnings:** 1
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

### problem_4

#### correct_recursive

- **Final Score:** 8.6500
- **Deterministic Score:** 8.6500
- **LLM Adjusted Score:** 8.6500
- **Test Pass Rate:** 100%
- **Tests:** 10/10 passed
- **Static Warnings:** 1
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### correct_stack

- **Final Score:** 8.7250
- **Deterministic Score:** 8.7250
- **LLM Adjusted Score:** 8.7250
- **Test Pass Rate:** 100%
- **Tests:** 10/10 passed
- **Static Warnings:** 1
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### edge_case_bug

- **Final Score:** 8.0750
- **Deterministic Score:** 8.0750
- **LLM Adjusted Score:** 8.0750
- **Test Pass Rate:** 90%
- **Tests:** 9/10 passed
- **Static Warnings:** 1
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### no_parens

- **Final Score:** 8.8250
- **Deterministic Score:** 8.8250
- **LLM Adjusted Score:** 8.8250
- **Test Pass Rate:** 90%
- **Tests:** 9/10 passed
- **Static Warnings:** 0
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### partial_correct

- **Final Score:** 6.1750
- **Deterministic Score:** 6.1750
- **LLM Adjusted Score:** 6.1750
- **Test Pass Rate:** 60%
- **Tests:** 6/10 passed
- **Static Warnings:** 2
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### style_poor

- **Final Score:** 7.1500
- **Deterministic Score:** 7.1500
- **LLM Adjusted Score:** 7.1500
- **Test Pass Rate:** 100%
- **Tests:** 10/10 passed
- **Static Warnings:** 22
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### wrong_precedence

- **Final Score:** 6.7250
- **Deterministic Score:** 6.7250
- **LLM Adjusted Score:** 6.7250
- **Test Pass Rate:** 70%
- **Tests:** 7/10 passed
- **Static Warnings:** 1
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

### problem_5

#### correct_alt

- **Final Score:** 8.9500
- **Deterministic Score:** 8.9500
- **LLM Adjusted Score:** 8.9500
- **Test Pass Rate:** 100%
- **Tests:** 10/10 passed
- **Static Warnings:** 0
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### correct_bfs

- **Final Score:** 8.9500
- **Deterministic Score:** 8.9500
- **LLM Adjusted Score:** 8.9500
- **Test Pass Rate:** 100%
- **Tests:** 10/10 passed
- **Static Warnings:** 0
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### edge_case_bug

- **Final Score:** 7.6500
- **Deterministic Score:** 7.6500
- **LLM Adjusted Score:** 7.6500
- **Test Pass Rate:** 80%
- **Tests:** 8/10 passed
- **Static Warnings:** 0
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### no_visited

- **Final Score:** 3.4500
- **Deterministic Score:** 3.4500
- **LLM Adjusted Score:** 3.4500
- **Test Pass Rate:** 0%
- **Tests:** 0/1 passed
- **Static Warnings:** 0
- **Timeout:** True
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### partial_correct

- **Final Score:** 8.3000
- **Deterministic Score:** 8.3000
- **LLM Adjusted Score:** 8.3000
- **Test Pass Rate:** 90%
- **Tests:** 9/10 passed
- **Static Warnings:** 0
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### style_poor

- **Final Score:** 7.7650
- **Deterministic Score:** 7.7650
- **LLM Adjusted Score:** 7.7650
- **Test Pass Rate:** 100%
- **Tests:** 10/10 passed
- **Static Warnings:** 3
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only

#### wrong_logic

- **Final Score:** 8.9000
- **Deterministic Score:** 8.9000
- **LLM Adjusted Score:** 8.9000
- **Test Pass Rate:** 90%
- **Tests:** 9/10 passed
- **Static Warnings:** 0
- **Timeout:** False
- **Sandbox Violation:** False
- **Issues:** LLM evaluation unavailable - using deterministic scores only
