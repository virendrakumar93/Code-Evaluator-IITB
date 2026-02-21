def climb_stairs(n: int) -> int:
    memo = {}

    def helper(steps):
        if steps <= 2:
            return steps
        if steps in memo:
            return memo[steps]
        memo[steps] = helper(steps - 1) + helper(steps - 2)
        return memo[steps]

    return helper(n)
