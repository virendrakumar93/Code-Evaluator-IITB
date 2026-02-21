def evaluate_expression(s: str) -> int:
    # BUG: Handles +, -, *, / with correct precedence but does NOT handle
    # parentheses at all. Will crash or give wrong results if '(' or ')' appear.
    stack = []
    num = 0
    sign = '+'
    i = 0
    n = len(s)

    while i < n:
        ch = s[i]

        if ch.isdigit():
            num = num * 10 + int(ch)

        if ch in '+-*/' or i == n - 1:
            if sign == '+':
                stack.append(num)
            elif sign == '-':
                stack.append(-num)
            elif sign == '*':
                stack.append(stack.pop() * num)
            elif sign == '/':
                top = stack.pop()
                stack.append(int(top / num))
            sign = ch
            num = 0

        i += 1

    return sum(stack)
