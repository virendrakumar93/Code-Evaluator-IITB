def evaluate_expression(s: str) -> int:
    # BUG: Evaluates strictly left to right, ignoring operator precedence.
    # e.g., "3+2*2" gives 10 instead of 7.
    tokens = []
    num = 0
    has_num = False
    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)
            has_num = True
        elif ch in '+-*/':
            if has_num:
                tokens.append(num)
                num = 0
                has_num = False
            tokens.append(ch)
        elif ch == '(':
            tokens.append(ch)
        elif ch == ')':
            if has_num:
                tokens.append(num)
                num = 0
                has_num = False
            tokens.append(ch)
    if has_num:
        tokens.append(num)

    # Resolve parentheses first by finding innermost pairs
    while '(' in tokens:
        # Find the last '('
        open_idx = None
        for idx, t in enumerate(tokens):
            if t == '(':
                open_idx = idx
        # Find the matching ')'
        close_idx = None
        for idx in range(open_idx + 1, len(tokens)):
            if tokens[idx] == ')':
                close_idx = idx
                break
        # Evaluate the sub-expression inside (left to right, no precedence)
        sub = tokens[open_idx + 1:close_idx]
        val = _eval_left_to_right(sub)
        tokens = tokens[:open_idx] + [val] + tokens[close_idx + 1:]

    return _eval_left_to_right(tokens)


def _eval_left_to_right(tokens):
    if not tokens:
        return 0
    result = tokens[0]
    i = 1
    while i < len(tokens):
        op = tokens[i]
        operand = tokens[i + 1]
        if op == '+':
            result += operand
        elif op == '-':
            result -= operand
        elif op == '*':
            result *= operand
        elif op == '/':
            result = int(result / operand)
        i += 2
    return result
