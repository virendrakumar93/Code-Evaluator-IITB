def shortest_path(graph: dict[int, list[int]], start: int, end: int) -> int:
    if start == end:
        return 0

    if start not in graph:
        return -1

    visited = set()

    def dfs(node, depth):
        if node == end:
            return depth

        visited.add(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                result = dfs(neighbor, depth + 1)
                if result != -1:
                    return result

        return -1

    return dfs(start, 0)
