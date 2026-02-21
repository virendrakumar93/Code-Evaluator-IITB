def climb_stairs(n: int) -> int:
    # Bug: does not handle n=1 or n=2 correctly.
    # The early return uses n-1 instead of n for small values,
    # returning 0 for n=1 and 1 for n=2.
    # The general DP logic for n >= 3 is correct.
    if n <= 2:
        return n - 1  # Wrong! Should return n. Returns 0 for n=1, 1 for n=2.

    prev2 = 1
    prev1 = 2

    for i in range(3, n + 1):
        current = prev1 + prev2
        prev2 = prev1
        prev1 = current

    return prev1
