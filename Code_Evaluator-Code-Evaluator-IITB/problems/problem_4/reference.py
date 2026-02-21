def evaluate_expression(s: str) -> int:
    """
    Evaluate a simple arithmetic expression string containing +, -, *, /,
    parentheses, digits, and spaces. Returns the integer result using
    integer division that truncates toward zero.

    Uses a stack-based approach with operator precedence handling.
    """
    i = 0
    n = len(s)

    def parse_expr():
        """Parse an expression handling + and - (lowest precedence)."""
        nonlocal i
        result = parse_term()
        while i < n:
            if s[i] == ' ':
                i += 1
                continue
            if s[i] == '+':
                i += 1
                result += parse_term()
            elif s[i] == '-':
                i += 1
                result -= parse_term()
            else:
                break
        return result

    def parse_term():
        """Parse a term handling * and / (higher precedence)."""
        nonlocal i
        result = parse_factor()
        while i < n:
            if s[i] == ' ':
                i += 1
                continue
            if s[i] == '*':
                i += 1
                result *= parse_factor()
            elif s[i] == '/':
                i += 1
                divisor = parse_factor()
                result = int(result / divisor)  # truncate toward zero
            else:
                break
        return result

    def parse_factor():
        """Parse a factor: a number or a parenthesized expression."""
        nonlocal i
        while i < n and s[i] == ' ':
            i += 1
        if s[i] == '(':
            i += 1  # skip '('
            result = parse_expr()
            while i < n and s[i] == ' ':
                i += 1
            i += 1  # skip ')'
            return result
        # Parse a number (possibly with leading unary minus)
        num = 0
        while i < n and s[i].isdigit():
            num = num * 10 + int(s[i])
            i += 1
        return num

    return parse_expr()
