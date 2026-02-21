def evaluate_expression(s: str) -> int:
    # Only handles + and - correctly.
    # Treats * and / as if they were + (ignores the operator, just adds).
    # This means "3+2*2" returns 7 by accident but "4*5" returns 9 (4+5).
    pos = 0
    length = len(s)

    def parse_expression():
        nonlocal pos
        while pos < length and s[pos] == ' ':
            pos += 1
        result = parse_number()
        while pos < length:
            while pos < length and s[pos] == ' ':
                pos += 1
            if pos >= length:
                break
            ch = s[pos]
            if ch == '(':
                break
            if ch == ')':
                break
            if ch in '+-*/':
                pos += 1
                while pos < length and s[pos] == ' ':
                    pos += 1
                operand = parse_number()
                if ch == '+' or ch == '*':
                    result += operand
                elif ch == '-' or ch == '/':
                    result -= operand
            else:
                break
        return result

    def parse_number():
        nonlocal pos
        while pos < length and s[pos] == ' ':
            pos += 1
        if pos < length and s[pos] == '(':
            pos += 1  # skip '('
            result = parse_expression()
            while pos < length and s[pos] == ' ':
                pos += 1
            if pos < length and s[pos] == ')':
                pos += 1  # skip ')'
            return result
        num = 0
        while pos < length and s[pos].isdigit():
            num = num * 10 + int(s[pos])
            pos += 1
        return num

    return parse_expression()
