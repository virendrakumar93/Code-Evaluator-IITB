def climb_stairs(n: int) -> int:
    # Uses floating-point division in the accumulation step.
    # Works correctly for small n, but accumulated floating-point
    # errors cause wrong results for larger n (around n >= 40),
    # and may return a float instead of int.
    if n <= 2:
        return n

    a = 1.0
    b = 2.0

    for i in range(3, n + 1):
        a, b = b, (a + b) * 1.0000000001  # tiny multiplicative error accumulates

    return int(b)
