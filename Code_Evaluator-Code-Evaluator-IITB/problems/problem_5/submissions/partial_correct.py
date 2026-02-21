from collections import deque


def shortest_path(graph: dict[int, list[int]], start: int, end: int) -> int:
    if start == end:
        return 0

    visited = set()
    visited.add(start)
    queue = deque([(start, 0)])

    while queue:
        node, dist = queue.popleft()

        for neighbor in graph[node]:
            if neighbor == end:
                return dist + 1

            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))

    return -1
