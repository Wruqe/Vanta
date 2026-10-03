import subprocess
import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from src.scanner import Scanner
from src.token_type import TokenType


class ScannerTests(unittest.TestCase):
    def scan(self, source):
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        return scanner, tokens

    def assert_types(self, source, expected):
        scanner, tokens = self.scan(source)
        self.assertEqual([], scanner.errors)
        self.assertEqual(expected, [token.type for token in tokens])
        return tokens

    def test_punctuation(self):
        self.assert_types(
            "(){} ,.;",
            [
                TokenType.LEFT_PAREN,
                TokenType.RIGHT_PAREN,
                TokenType.LEFT_BRACE,
                TokenType.RIGHT_BRACE,
                TokenType.COMMA,
                TokenType.DOT,
                TokenType.SEMICOLON,
                TokenType.EOF,
            ],
        )

    def test_arithmetic_and_comparison_operators(self):
        self.assert_types(
            "+ - * / ! != = == < <= > >=",
            [
                TokenType.PLUS,
                TokenType.MINUS,
                TokenType.STAR,
                TokenType.SLASH,
                TokenType.BANG,
                TokenType.BANG_EQUAL,
                TokenType.EQUAL,
                TokenType.EQUAL_EQUAL,
                TokenType.LESS,
                TokenType.LESS_EQUAL,
                TokenType.GREATER,
                TokenType.GREATER_EQUAL,
                TokenType.EOF,
            ],
        )

    def test_every_keyword(self):
        tokens = self.assert_types(
            "let fn if else while for return true false null print",
            [
                TokenType.LET,
                TokenType.FN,
                TokenType.IF,
                TokenType.ELSE,
                TokenType.WHILE,
                TokenType.FOR,
                TokenType.RETURN,
                TokenType.TRUE,
                TokenType.FALSE,
                TokenType.NULL,
                TokenType.PRINT,
                TokenType.EOF,
            ],
        )
        self.assertIs(tokens[7].literal, True)
        self.assertIs(tokens[8].literal, False)
        self.assertIsNone(tokens[9].literal)

    def test_identifiers(self):
        tokens = self.assert_types(
            "alpha _private name2 letdown",
            [TokenType.IDENTIFIER] * 4 + [TokenType.EOF],
        )
        self.assertEqual(
            ["alpha", "_private", "name2", "letdown"],
            [token.lexeme for token in tokens[:-1]],
        )

    def test_integers_decimals_and_dot_boundary(self):
        tokens = self.assert_types(
            "10 123 3.14 0.5 1.foo",
            [
                TokenType.NUMBER,
                TokenType.NUMBER,
                TokenType.NUMBER,
                TokenType.NUMBER,
                TokenType.NUMBER,
                TokenType.DOT,
                TokenType.IDENTIFIER,
                TokenType.EOF,
            ],
        )
        self.assertEqual([10, 123, 3.14, 0.5, 1], [t.literal for t in tokens[:5]])

    def test_strings_and_multiline_line_tracking(self):
        tokens = self.assert_types(
            '"hello world" "line one\nline two" next',
            [TokenType.STRING, TokenType.STRING, TokenType.IDENTIFIER, TokenType.EOF],
        )
        self.assertEqual("hello world", tokens[0].literal)
        self.assertEqual("line one\nline two", tokens[1].literal)
        self.assertEqual([1, 2, 2, 2], [token.line for token in tokens])

    def test_comments_whitespace_newlines_and_eof(self):
        tokens = self.assert_types(
            "let // ignored\r\n\tname / 2",
            [TokenType.LET, TokenType.IDENTIFIER, TokenType.SLASH, TokenType.NUMBER, TokenType.EOF],
        )
        self.assertEqual([1, 2, 2, 2, 2], [token.line for token in tokens])
        self.assertEqual("", tokens[-1].lexeme)

    def test_unterminated_string_is_reported(self):
        scanner, tokens = self.scan('"not closed')
        self.assertEqual([(1, "Unterminated string.")], scanner.errors)
        self.assertEqual([TokenType.EOF], [token.type for token in tokens])

    def test_unexpected_character_is_reported_and_scanning_continues(self):
        scanner, tokens = self.scan("@ let")
        self.assertEqual([(1, "Unexpected character '@'.")], scanner.errors)
        self.assertEqual([TokenType.LET, TokenType.EOF], [token.type for token in tokens])

    def test_larger_program_fixture(self):
        source = (REPOSITORY_ROOT / "test/lab1/basic.vanta").read_text(encoding="utf-8")
        scanner, tokens = self.scan(source)
        self.assertEqual([], scanner.errors)
        self.assertEqual(TokenType.FN, tokens[0].type)
        self.assertIn(TokenType.GREATER_EQUAL, [token.type for token in tokens])
        self.assertIn(TokenType.STRING, [token.type for token in tokens])
        self.assertEqual(TokenType.EOF, tokens[-1].type)


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
        result = self.run_main(("test/lab1/basic.vanta",))
        self.assertEqual(0, result.returncode)
        self.assertIn("FN", result.stdout)
        self.assertIn("STRING", result.stdout)
        self.assertIn("EOF", result.stdout)
        self.assertEqual("", result.stderr)

    def test_source_file_error_status(self):
        result = self.run_main(("test/lab1/errors.vanta",))
        self.assertEqual(65, result.returncode)
        self.assertIn("Unexpected character", result.stderr)
        self.assertIn("Unterminated string", result.stderr)

    def test_interactive_mode_recovers_after_error(self):
        result = self.run_main(input_text="@\nlet ok = 1;\n")
        self.assertEqual(0, result.returncode)
        self.assertIn("Unexpected character", result.stderr)
        self.assertIn("LET", result.stdout)
        self.assertIn("IDENTIFIER", result.stdout)
        self.assertGreaterEqual(result.stdout.count("EOF"), 2)

    def test_invalid_argument_count(self):
        result = self.run_main(("one.vanta", "two.vanta"))
        self.assertEqual(64, result.returncode)
        self.assertIn("Usage:", result.stderr)


if __name__ == "__main__":
    unittest.main()
