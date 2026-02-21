def generate_parentheses(n: int) -> list[str]:
    # Bug 1: n=0 returns [] instead of [""]
    # Bug 2: n=1 returns [""] (empty string) because the logic
    #         adds an extra empty string when open/close both start at 1
    if n <= 0:
        return []

    result = []

    def backtrack(current, open_count, close_count):
        if open_count == 0 and close_count == 0:
            result.append(current)
            return
        if open_count > 0:
            backtrack(current + "(", open_count - 1, close_count)
        if close_count > open_count:
            backtrack(current + ")", open_count, close_count - 1)

    backtrack("", n, n)
    return sorted(result)
