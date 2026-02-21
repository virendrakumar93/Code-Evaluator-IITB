def evaluate_expression(s: str) -> int:
    pos = 0
    length = len(s)

    def parse_expression():
        nonlocal pos
        result = parse_term()
        while pos < length:
            if s[pos] == ' ':
                pos += 1
                continue
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
            if s[pos] == ' ':
                pos += 1
                continue
            if s[pos] == '*':
                pos += 1
                result *= parse_factor()
            elif s[pos] == '/':
                pos += 1
                divisor = parse_factor()
                result = int(result / divisor)
            else:
                break
        return result

    def parse_factor():
        nonlocal pos
        while pos < length and s[pos] == ' ':
            pos += 1
        if s[pos] == '(':
            pos += 1  # skip '('
            result = parse_expression()
            while pos < length and s[pos] == ' ':
                pos += 1
            pos += 1  # skip ')'
            return result
        num = 0
        while pos < length and s[pos].isdigit():
            num = num * 10 + int(s[pos])
            pos += 1
        return num

    return parse_expression()
