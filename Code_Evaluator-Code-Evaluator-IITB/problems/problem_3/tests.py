import unittest


class TestClimbStairs(unittest.TestCase):
    """Test cases for the climb_stairs function."""

    def test_n_equals_1(self):
        """Base case: only one step, one way to climb."""
        self.assertEqual(climb_stairs(1), 1)

    def test_n_equals_2(self):
        """Two steps: either [1,1] or [2]."""
        self.assertEqual(climb_stairs(2), 2)

    def test_n_equals_3(self):
        """Three steps: [1,1,1], [1,2], [2,1]."""
        self.assertEqual(climb_stairs(3), 3)

    def test_n_equals_4(self):
        """Four steps: 5 distinct ways."""
        self.assertEqual(climb_stairs(4), 5)

    def test_n_equals_5(self):
        """Five steps: 8 distinct ways."""
        self.assertEqual(climb_stairs(5), 8)

    def test_n_equals_10(self):
        """Ten steps: 89 distinct ways."""
        self.assertEqual(climb_stairs(10), 89)

    def test_n_equals_20(self):
        """Twenty steps: 10946 distinct ways."""
        self.assertEqual(climb_stairs(20), 10946)

    def test_edge_case_n_equals_1(self):
        """Edge case: minimum valid input."""
        result = climb_stairs(1)
        self.assertEqual(result, 1)
        self.assertGreater(result, 0)

    def test_n_equals_45(self):
        """Upper bound: n=45 should return 1836311903."""
        self.assertEqual(climb_stairs(45), 1836311903)

    def test_returns_int(self):
        """Result should always be an integer type."""
        result = climb_stairs(10)
        self.assertIsInstance(result, int)


if __name__ == "__main__":
    unittest.main()
