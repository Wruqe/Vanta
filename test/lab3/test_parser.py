import subprocess
import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from src.ast_printer import AstPrinter
from src.parser import Parser
from src.scanner import Scanner


class ParserTests(unittest.TestCase):
    def parse(self, source):
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        self.assertEqual([], scanner.errors)

        parser = Parser(tokens)
        expression = parser.parse()
        printed = None if expression is None else AstPrinter().print(expression)
        return parser, printed

    def assert_ast(self, source, expected):
        parser, actual = self.parse(source)
        self.assertEqual([], parser.errors)
        self.assertEqual(expected, actual)

    def assert_parse_error(self, source, expected_location, expected_message):
        parser, actual = self.parse(source)
        self.assertIsNone(actual)
        self.assertEqual(1, len(parser.errors))
        line, location, message = parser.errors[0]
        self.assertEqual(1, line)
        self.assertEqual(expected_location, location)
        self.assertEqual(expected_message, message)

    def test_every_literal_type(self):
        cases = {
            "10": "10",
            "3.14": "3.14",
            '"hello"': '"hello"',
            "true": "true",
            "false": "false",
            "null": "null",
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assert_ast(source, expected)

    def test_every_binary_operator(self):
        cases = {
            "+": "(+ 8 2)",
            "-": "(- 8 2)",
            "*": "(* 8 2)",
            "/": "(/ 8 2)",
            "==": "(== 8 2)",
            "!=": "(!= 8 2)",
            ">": "(> 8 2)",
            ">=": "(>= 8 2)",
            "<": "(< 8 2)",
            "<=": "(<= 8 2)",
            "and": "(and true false)",
            "or": "(or true false)",
        }
        for operator, expected in cases.items():
            left = "true" if operator in ("and", "or") else "8"
            right = "false" if operator in ("and", "or") else "2"
            with self.subTest(operator=operator):
                self.assert_ast(f"{left} {operator} {right}", expected)

    def test_precedence(self):
        self.assert_ast(
            "false or true and 1 + 2 * 3 == 7",
            "(or false (and true (== (+ 1 (* 2 3)) 7)))",
        )

    def test_left_associativity(self):
        self.assert_ast("10 - 3 - 2", "(- (- 10 3) 2)")

    def test_unary_and_nested_grouping(self):
        self.assert_ast(
            "!!false or -(3 + (4 * 2)) < 0",
            "(or (! (! false)) (< (- (group (+ 3 (group (* 4 2))))) 0))",
        )

    def test_missing_operand(self):
        self.assert_parse_error("1 +", "at end", "Expected expression.")

    def test_missing_left_operand(self):
        self.assert_parse_error("+ 1", "at '+'", "Expected expression.")

    def test_missing_right_parenthesis(self):
        self.assert_parse_error(
            "(1 + 2",
            "at end",
            "Expected ')' after expression.",
        )

    def test_unmatched_right_parenthesis(self):
        self.assert_parse_error(
            "1 + 2)",
            "at ')'",
            "Unexpected token after expression.",
        )

    def test_unexpected_token(self):
        self.assert_parse_error("let", "at 'let'", "Expected expression.")

    def test_trailing_tokens(self):
        self.assert_parse_error(
            "1 2",
            "at '2'",
            "Unexpected token after expression.",
        )


class CommandLineTests(unittest.TestCase):
    def run_main(self, arguments=(), input_text=None):
        return subprocess.run(
            [sys.executable, "src/main.py", *arguments],
            cwd=REPOSITORY_ROOT,
            input=input_text,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_source_file_mode(self):
        result = self.run_main(("test/lab3/precedence.vanta",))
        self.assertEqual(0, result.returncode)
        self.assertEqual(
            "(or false (and true (== (+ 1 (* 2 3)) 7)))\n",
            result.stdout,
        )
        self.assertEqual("", result.stderr)

    def test_source_file_syntax_error_prints_no_ast(self):
        result = self.run_main(("test/lab3/missing_right_paren.vanta",))
        self.assertEqual(65, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertIn("[line 2] Error at end", result.stderr)
        self.assertIn("Expected ')' after expression", result.stderr)

    def test_source_file_lexical_error_prints_no_ast(self):
        result = self.run_main(("test/lab3/lexical_error.vanta",))
        self.assertEqual(65, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertIn("[line 1] Error: Unexpected character '@'.", result.stderr)

    def test_interactive_mode_recovers_after_syntax_and_lexical_errors(self):
        result = self.run_main(input_text="1 +\n@\n2 * 3\n")
        self.assertEqual(0, result.returncode)
        self.assertIn("Error at end: Expected expression.", result.stderr)
        self.assertIn("Unexpected character '@'.", result.stderr)
        self.assertIn("(* 2 3)", result.stdout)
        self.assertNotIn("(+ 1", result.stdout)

    def test_legacy_token_mode(self):
        result = self.run_main(("--tokens", "test/lab1/operators.vanta"))
        self.assertEqual(0, result.returncode)
        self.assertIn("LEFT_PAREN", result.stdout)
        self.assertIn("EOF", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
