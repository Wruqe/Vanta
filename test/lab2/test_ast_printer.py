import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from ast_examples import EXAMPLES
from src.ast_printer import AstPrinter
from src.expr import Binary, Expr, Grouping, Literal, Unary
from src.token_type import TokenType


EXPECTED_OUTPUTS = {
    "arithmetic": "(* (- 123) (group (- (+ 45.67 (/ 8 2)) 1)))",
    "comparison": (
        "(and (and (!= \"alpha\" \"beta\") (>= 10 5)) "
        "(and (== (< 3 4) true) (== (> 6 2) (<= 7 7))))"
    ),
    "logical": "(or (and true (! false)) (== null null))",
}


class AstPrinterTests(unittest.TestCase):
    def setUp(self):
        self.printer = AstPrinter()
        self.examples = dict(EXAMPLES)

    def test_hard_coded_examples(self):
        actual = {
            name: self.printer.print(expression)
            for name, expression in EXAMPLES
        }
        self.assertEqual(EXPECTED_OUTPUTS, actual)

    def test_examples_cover_every_expression_class(self):
        expression_types = set()

        def visit(expression):
            expression_types.add(type(expression))
            if isinstance(expression, Binary):
                visit(expression.left)
                visit(expression.right)
            elif isinstance(expression, Grouping):
                visit(expression.expression)
            elif isinstance(expression, Unary):
                visit(expression.right)

        for expression in self.examples.values():
            visit(expression)

        self.assertEqual({Binary, Grouping, Literal, Unary}, expression_types)

    def test_examples_cover_every_expression_operator(self):
        operator_types = set()

        def visit(expression):
            if isinstance(expression, Binary):
                operator_types.add(expression.operator.type)
                visit(expression.left)
                visit(expression.right)
            elif isinstance(expression, Grouping):
                visit(expression.expression)
            elif isinstance(expression, Unary):
                operator_types.add(expression.operator.type)
                visit(expression.right)

        for expression in self.examples.values():
            visit(expression)

        self.assertEqual(
            {
                TokenType.PLUS,
                TokenType.MINUS,
                TokenType.STAR,
                TokenType.SLASH,
                TokenType.BANG,
                TokenType.BANG_EQUAL,
                TokenType.EQUAL_EQUAL,
                TokenType.GREATER,
                TokenType.GREATER_EQUAL,
                TokenType.LESS,
                TokenType.LESS_EQUAL,
                TokenType.AND,
                TokenType.OR,
            },
            operator_types,
        )

    def test_examples_cover_every_literal_type(self):
        literal_types = set()

        def visit(expression):
            if isinstance(expression, Literal):
                literal_types.add(type(expression.value))
            elif isinstance(expression, Binary):
                visit(expression.left)
                visit(expression.right)
            elif isinstance(expression, Grouping):
                visit(expression.expression)
            elif isinstance(expression, Unary):
                visit(expression.right)

        for expression in self.examples.values():
            visit(expression)

        self.assertEqual({int, float, str, bool, type(None)}, literal_types)

    def test_nodes_retain_their_required_fields(self):
        arithmetic = self.examples["arithmetic"]
        self.assertIsInstance(arithmetic, Expr)
        self.assertEqual("*", arithmetic.operator.lexeme)
        self.assertIsInstance(arithmetic.left, Unary)
        self.assertIsInstance(arithmetic.right, Grouping)
        self.assertEqual(123, arithmetic.left.right.value)

    def test_string_literal_output_is_unambiguous_and_escaped(self):
        expression = Literal('line one\n"line two"')
        self.assertEqual('"line one\\n\\"line two\\""', self.printer.print(expression))


if __name__ == "__main__":
    unittest.main(verbosity=2)
