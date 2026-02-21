def climb_stairs(n: int) -> int:
    """
    Calculate the number of distinct ways to climb a staircase of n steps,
    where each time you can climb 1 or 2 steps.

    Uses iterative DP with O(n) time and O(1) space.
    This is equivalent to computing the (n+1)-th Fibonacci number.

    Args:
        n: The number of steps in the staircase (1 <= n <= 45).

    Returns:
        The number of distinct ways to reach the top.
    """
    if n <= 2:
        return n

    prev2 = 1  # ways to climb 1 step
    prev1 = 2  # ways to climb 2 steps

    for _ in range(3, n + 1):
        current = prev1 + prev2
        prev2 = prev1
        prev1 = current

    return prev1
