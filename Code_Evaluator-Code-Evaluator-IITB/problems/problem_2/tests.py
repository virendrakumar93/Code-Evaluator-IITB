import unittest


class TestGenerateParentheses(unittest.TestCase):
    def test_n_zero(self):
        result = generate_parentheses(0)
        self.assertEqual(result, [""])

    def test_n_one(self):
        self.assertEqual(generate_parentheses(1), ["()"])

    def test_n_two(self):
        self.assertEqual(sorted(generate_parentheses(2)), ["(())", "()()"])

    def test_n_three(self):
        expected = ["((()))", "(()())", "(())()", "()(())", "()()()"]
        self.assertEqual(sorted(generate_parentheses(3)), expected)

    def test_n_four_length(self):
        result = generate_parentheses(4)
        self.assertEqual(len(result), 14)

    def test_all_valid_parentheses(self):
        for combo in generate_parentheses(4):
            depth = 0
            for ch in combo:
                if ch == "(":
                    depth += 1
                else:
                    depth -= 1
                self.assertGreaterEqual(depth, 0, f"Invalid parentheses: {combo}")
            self.assertEqual(depth, 0, f"Unbalanced parentheses: {combo}")

    def test_no_duplicates(self):
        result = generate_parentheses(4)
        self.assertEqual(len(result), len(set(result)))

    def test_sorted_output(self):
        result = generate_parentheses(3)
        self.assertEqual(result, sorted(result))

    def test_correct_string_lengths(self):
        for n in range(1, 5):
            for combo in generate_parentheses(n):
                self.assertEqual(len(combo), 2 * n)

    def test_n_five_length(self):
        result = generate_parentheses(5)
        self.assertEqual(len(result), 42)
