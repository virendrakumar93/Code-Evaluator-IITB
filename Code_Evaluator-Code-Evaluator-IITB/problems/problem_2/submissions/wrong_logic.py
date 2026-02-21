def generate_parentheses(n: int) -> list[str]:
    if n == 0:
        return [""]

    result = []

    def generate(current, remaining_open, remaining_close):
        if remaining_open == 0 and remaining_close == 0:
            result.append(current)
            return
        # Bug: allows closing before opening, generating invalid combos like ")("
        if remaining_open > 0:
            generate(current + "(", remaining_open - 1, remaining_close)
        if remaining_close > 0:
            generate(current + ")", remaining_open, remaining_close - 1)

    generate("", n, n)
    return sorted(result)
