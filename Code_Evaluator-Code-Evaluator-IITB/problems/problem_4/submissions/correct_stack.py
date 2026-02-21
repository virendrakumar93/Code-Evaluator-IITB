def evaluate_expression(s: str) -> int:
    stack = []
    num = 0
    sign = '+'
    i = 0
    n = len(s)

    while i < n:
        ch = s[i]

        if ch.isdigit():
            num = num * 10 + int(ch)

        if ch == '(':
            # Find the matching closing parenthesis
            depth = 1
            j = i + 1
            while depth > 0:
                if s[j] == '(':
                    depth += 1
                elif s[j] == ')':
                    depth -= 1
                j += 1
            # Recursively evaluate the sub-expression inside parentheses
            num = evaluate_expression(s[i + 1:j - 1])
            i = j - 1

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
