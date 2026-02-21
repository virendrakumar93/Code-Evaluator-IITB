def generate_parentheses(n: int) -> list[str]:
    if n == 0:
        return [""]

    # Only generates fully nested patterns, misses interleaved ones.
    # For n=3, produces ["((()))", "(())()", "()()()"] but misses
    # "(()())" and "()(())"
    result = []

    def build(pairs_left, suffix):
        if pairs_left == 0:
            result.append(suffix)
            return
        # Strategy: take k pairs and nest them, then recurse on the rest
        for k in range(1, pairs_left + 1):
            nested = "(" * k + ")" * k
            build(pairs_left - k, nested + suffix)

    build(n, "")
    # Deduplicate and sort
    return sorted(set(result))
