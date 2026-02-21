# Problem 3: Climbing Stairs

You are climbing a staircase with `n` steps. Each time you can climb 1 or 2 steps. How many distinct ways can you reach the top?

## Function Signature

```python
def climb_stairs(n: int) -> int:
```

## Examples

| Input | Output |
|-------|--------|
| n = 1 | 1      |
| n = 2 | 2      |
| n = 3 | 3      |
| n = 5 | 8      |

## Explanation

- **n = 1**: There is only one way to climb: `[1]`.
- **n = 2**: There are two ways: `[1, 1]` or `[2]`.
- **n = 3**: There are three ways: `[1, 1, 1]`, `[1, 2]`, or `[2, 1]`.
- **n = 5**: There are eight ways to reach the top.

## Constraints

- `1 <= n <= 45`

## Expected Complexity

- **Time**: O(n)
- **Space**: O(1)
