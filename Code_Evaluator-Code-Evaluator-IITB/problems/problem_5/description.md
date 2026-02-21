# Problem 5: Shortest Path in Unweighted Graph (BFS)

Given an unweighted undirected graph represented as an adjacency list and two nodes `start` and `end`, find the length of the shortest path between them. Return -1 if no path exists.

## Function Signature

```python
def shortest_path(graph: dict[int, list[int]], start: int, end: int) -> int:
```

where `graph` maps node -> list of neighbors.

## Examples

- `graph={0:[1,2], 1:[0,3], 2:[0,3], 3:[1,2]}`, `start=0`, `end=3` -> `2`

## Constraints

- Nodes are integers `0..n-1`.
- The graph may be disconnected.
- Expected time complexity: O(V+E).
