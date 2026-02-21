def shortest_path(graph: dict[int, list[int]], start: int, end: int) -> int:
    if start == end:
        return 0

    if start not in graph:
        return -1

    visited = set()
    visited.add(start)
    queue = [(start, 0)]

    while queue:
        node, dist = queue.pop(0)

        for neighbor in graph.get(node, []):
            if neighbor == end:
                return dist + 1

            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))

    return -1
