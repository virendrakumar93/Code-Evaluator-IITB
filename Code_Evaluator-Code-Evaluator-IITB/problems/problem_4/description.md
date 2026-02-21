# Problem 4: Evaluate Simple Arithmetic Expression

## Description
Given a string containing a simple arithmetic expression with `+`, `-`, `*`, `/` and parentheses, evaluate it and return the integer result. Use integer division (truncate toward zero).

## Function Signature
```python
def evaluate_expression(s: str) -> int:
```

## Examples
- Input: `"3+2*2"` → Output: `7`
- Input: `" 3/2 "` → Output: `1`
- Input: `" 3+5 / 2 "` → Output: `5`
- Input: `"(1+(4+5+2)-3)+(6+8)"` → Output: `23`

## Constraints
- `s` contains digits, `+`, `-`, `*`, `/`, `(`, `)`, and spaces.
- The expression is always valid.
- Division is integer division that truncates toward zero.

## Expected Complexity
- Time: O(n)
- Space: O(n)
