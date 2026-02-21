from collections import deque


def shortest_path(graph: dict[int, list[int]], start: int, end: int) -> int:
    """Find the length of the shortest path between start and end in an unweighted graph.

    Uses BFS to guarantee shortest path in an unweighted graph.
    Returns -1 if no path exists.
    """
    if start == end:
        return 0

    if start not in graph:
        return -1

    visited = set()
    visited.add(start)
    queue = deque([(start, 0)])

    while queue:
        node, distance = queue.popleft()

        for neighbor in graph.get(node, []):
            if neighbor == end:
                return distance + 1

            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, distance + 1))

    return -1
