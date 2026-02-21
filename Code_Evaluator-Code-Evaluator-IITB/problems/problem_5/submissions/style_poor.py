from collections import deque
def shortest_path(graph: dict[int, list[int]], start: int, end: int) -> int:
    if start==end: return 0
    if start not in graph: return -1
    v=set()
    v.add(start)
    q=deque([(start,0)])
    while q:
        n,d=q.popleft()
        for x in graph.get(n,[]):
            if x==end: return d+1
            if x not in v:
                v.add(x)
                q.append((x,d+1))
    return -1
