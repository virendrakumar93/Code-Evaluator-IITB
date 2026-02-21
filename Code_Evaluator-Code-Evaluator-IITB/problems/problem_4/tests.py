import unittest


class TestEvaluateExpression(unittest.TestCase):
    def test_simple_addition(self):
        self.assertEqual(evaluate_expression("1+1"), 2)

    def test_simple_subtraction(self):
        self.assertEqual(evaluate_expression("10-3"), 7)

    def test_simple_multiplication(self):
        self.assertEqual(evaluate_expression("4*5"), 20)

    def test_simple_division(self):
        self.assertEqual(evaluate_expression("3/2"), 1)

    def test_mixed_operations_precedence(self):
        self.assertEqual(evaluate_expression("3+2*2"), 7)

    def test_parentheses(self):
        self.assertEqual(evaluate_expression("(1+(4+5+2)-3)+(6+8)"), 23)

    def test_nested_parentheses(self):
        self.assertEqual(evaluate_expression("((2+3)*(4-1))"), 15)

    def test_spaces_in_expression(self):
        self.assertEqual(evaluate_expression(" 3 + 5 / 2 "), 5)

    def test_negative_intermediate_result(self):
        self.assertEqual(evaluate_expression("1-2+3*4"), 11)

    def test_zero_edge_case(self):
        self.assertEqual(evaluate_expression("0"), 0)
