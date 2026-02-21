def generate_parentheses(n: int) -> list[str]:
    if n == 0:
        return [""]

    # DP approach: build solutions for each i from 0 to n
    # For each pair count i, a valid sequence is "(" + a + ")" + b
    # where a has j pairs and b has i-1-j pairs, for j in [0, i-1]
    dp = [[] for _ in range(n + 1)]
    dp[0] = [""]

    for i in range(1, n + 1):
        for j in range(i):
            for a in dp[j]:
                for b in dp[i - 1 - j]:
                    dp[i].append("(" + a + ")" + b)

    return sorted(dp[n])
