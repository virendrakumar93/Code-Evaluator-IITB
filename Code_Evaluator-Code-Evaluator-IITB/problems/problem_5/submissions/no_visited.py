from collections import deque


def shortest_path(graph: dict[int, list[int]], start: int, end: int) -> int:
    if start == end:
        return 0

    if start not in graph:
        return -1

    queue = deque([(start, 0)])

    while queue:
        node, dist = queue.popleft()

        for neighbor in graph.get(node, []):
            if neighbor == end:
                return dist + 1

            queue.append((neighbor, dist + 1))

    return -1
