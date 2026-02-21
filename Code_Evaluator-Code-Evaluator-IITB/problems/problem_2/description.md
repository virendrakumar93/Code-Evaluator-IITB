# Problem 2: Generate Balanced Parentheses

## Description
Given `n` pairs of parentheses, write a function to generate all combinations of well-formed parentheses.

A combination is "well-formed" if every opening parenthesis `(` has a corresponding closing parenthesis `)` and they are properly nested.

## Function Signature
```python
def generate_parentheses(n: int) -> list[str]:
```

## Examples
- Input: n = 1 → Output: ["()"]
- Input: n = 2 → Output: ["(())", "()()"]
- Input: n = 3 → Output: ["((()))", "(()())", "(())()", "()(())", "()()()"]

## Constraints
- 1 <= n <= 8
- Return the combinations in sorted (lexicographic) order.

## Expected Complexity
- Time: O(4^n / √n) — the nth Catalan number
- Space: O(n) recursion depth, O(4^n / √n) for the output
