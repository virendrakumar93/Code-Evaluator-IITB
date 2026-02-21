import unittest


class TestShortestPath(unittest.TestCase):
    """Test cases for shortest_path function."""

    def test_direct_neighbor(self):
        """Two nodes directly connected should have distance 1."""
        graph = {0: [1, 2], 1: [0], 2: [0]}
        self.assertEqual(shortest_path(graph, 0, 1), 1)

    def test_two_hops(self):
        """Path requiring two hops through intermediate node."""
        graph = {0: [1, 2], 1: [0, 3], 2: [0, 3], 3: [1, 2]}
        self.assertEqual(shortest_path(graph, 0, 3), 2)

    def test_no_path_disconnected(self):
        """Disconnected graph where no path exists should return -1."""
        graph = {0: [1], 1: [0], 2: [3], 3: [2]}
        self.assertEqual(shortest_path(graph, 0, 3), -1)

    def test_same_start_and_end(self):
        """Start equals end should return 0."""
        graph = {0: [1], 1: [0]}
        self.assertEqual(shortest_path(graph, 0, 0), 0)

    def test_linear_graph(self):
        """Linear chain: 0-1-2-3-4, distance from 0 to 4 is 4."""
        graph = {
            0: [1],
            1: [0, 2],
            2: [1, 3],
            3: [2, 4],
            4: [3],
        }
        self.assertEqual(shortest_path(graph, 0, 4), 4)

    def test_cycle_graph(self):
        """Cycle graph: 0-1-2-3-0, shortest from 0 to 2 is 2 (not 2 via the other way which is also 2)."""
        graph = {
            0: [1, 3],
            1: [0, 2],
            2: [1, 3],
            3: [2, 0],
        }
        self.assertEqual(shortest_path(graph, 0, 2), 2)

    def test_single_node(self):
        """Graph with a single node, start==end."""
        graph = {0: []}
        self.assertEqual(shortest_path(graph, 0, 0), 0)

    def test_larger_graph(self):
        """Larger graph where DFS would follow a long path but BFS finds the short one."""
        graph = {
            0: [1, 4],
            1: [0, 2],
            2: [1, 3],
            3: [2, 4],
            4: [0, 3],
        }
        # Shortest: 0 -> 4 = 1 hop
        # DFS would go 0 -> 1 -> 2 -> 3 -> 4 = 4 hops
        self.assertEqual(shortest_path(graph, 0, 4), 1)

    def test_empty_neighbors(self):
        """Node exists in graph but has no neighbors; should return -1 for unreachable target."""
        graph = {0: [], 1: []}
        self.assertEqual(shortest_path(graph, 0, 1), -1)

    def test_node_not_in_graph(self):
        """Start node not present in graph keys should return -1."""
        graph = {0: [1], 1: [0]}
        self.assertEqual(shortest_path(graph, 5, 0), -1)


if __name__ == "__main__":
    unittest.main()
