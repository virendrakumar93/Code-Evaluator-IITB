import unittest


class TestTwoSum(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(sorted(two_sum([2, 7, 11, 15], 9)), [0, 1])

    def test_middle_elements(self):
        self.assertEqual(sorted(two_sum([3, 2, 4], 6)), [1, 2])

    def test_duplicates(self):
        self.assertEqual(sorted(two_sum([3, 3], 6)), [0, 1])

    def test_negative_numbers(self):
        self.assertEqual(sorted(two_sum([-1, -2, -3, -4, -5], -8)), [2, 4])

    def test_mixed_signs(self):
        self.assertEqual(sorted(two_sum([-3, 4, 3, 90], 0)), [0, 2])

    def test_large_numbers(self):
        self.assertEqual(sorted(two_sum([1000000000, -1000000000], 0)), [0, 1])

    def test_single_pair(self):
        self.assertEqual(sorted(two_sum([1, 2], 3)), [0, 1])

    def test_zero_target(self):
        self.assertEqual(sorted(two_sum([0, 4, 3, 0], 0)), [0, 3])

    def test_larger_array(self):
        result = sorted(two_sum([1, 5, 8, 3, 9, 2], 11))
        self.assertIn(result, [[1, 4], [2, 3]])

    def test_first_and_last(self):
        self.assertEqual(sorted(two_sum([10, 1, 2, 3, 5], 15)), [0, 4])
