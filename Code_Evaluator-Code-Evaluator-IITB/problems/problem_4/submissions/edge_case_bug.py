def evaluate_expression(s: str) -> int:
    # BUG 1: Does not strip/skip spaces properly -- spaces break number parsing.
    # BUG 2: Uses Python's // for division which floors toward negative infinity
    #         instead of truncating toward zero (e.g., -3//2 = -2 instead of -1).
    pos = 0
    length = len(s)

    def parse_expression():
        nonlocal pos
        result = parse_term()
        while pos < length:
            # BUG: no space skipping here
            if s[pos] == '+':
                pos += 1
                result += parse_term()
            elif s[pos] == '-':
                pos += 1
                result -= parse_term()
            else:
                break
        return result

    def parse_term():
        nonlocal pos
        result = parse_factor()
        while pos < length:
            # BUG: no space skipping here
            if s[pos] == '*':
                pos += 1
                result *= parse_factor()
            elif s[pos] == '/':
                pos += 1
                divisor = parse_factor()
                # BUG: uses // which floors toward negative infinity
                result = result // divisor
            else:
                break
        return result

    def parse_factor():
        nonlocal pos
        # BUG: no space skipping here -- spaces will cause index errors
        if pos < length and s[pos] == '(':
            pos += 1
            result = parse_expression()
            if pos < length and s[pos] == ')':
                pos += 1
            return result
        num = 0
        while pos < length and s[pos].isdigit():
            num = num * 10 + int(s[pos])
            pos += 1
        return num

    return parse_expression()
