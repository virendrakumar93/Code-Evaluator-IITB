def generate_parentheses(n: int) -> list[str]:
    if n == 0:
        return [""]

    from itertools import product

    # Generate ALL possible strings of length 2n using '(' and ')',
    # then filter for valid ones. This is O(2^(2n)) which is exponentially
    # slower than the Catalan-number backtracking approach.
    valid = []
    for combo in product("()", repeat=2 * n):
        s = "".join(combo)
        depth = 0
        is_valid = True
        for ch in s:
            if ch == "(":
                depth += 1
            else:
                depth -= 1
            if depth < 0:
                is_valid = False
                break
        if is_valid and depth == 0:
            valid.append(s)

    return sorted(valid)
