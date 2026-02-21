def climb_stairs(n: int) -> int:
    # Off-by-one error: wrong base cases lead to incorrect results.
    # Uses dp[0] = 0 and dp[1] = 1 instead of the correct base cases,
    # which shifts all results down by one position in the Fibonacci sequence.
    if n <= 1:
        return 1

    prev2 = 0
    prev1 = 1

    for i in range(2, n + 1):
        current = prev1 + prev2
        prev2 = prev1
        prev1 = current

    return prev1
