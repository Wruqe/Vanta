import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT))

from src.ast_printer import AstPrinter
from src.expr import Binary, Grouping, Literal, Unary
from src.token_type import TokenType
from src.vanta_token import Token


def operator(token_type, lexeme):
    return Token(token_type, lexeme, None, 1)


def arithmetic_tree():
    return Binary(
        Unary(operator(TokenType.MINUS, "-"), Literal(123)),
        operator(TokenType.STAR, "*"),
        Grouping(
            Binary(
                Binary(
                    Literal(45.67),
                    operator(TokenType.PLUS, "+"),
                    Binary(
                        Literal(8),
                        operator(TokenType.SLASH, "/"),
                        Literal(2),
                    ),
                ),
                operator(TokenType.MINUS, "-"),
                Literal(1),
            )
        ),
    )


def comparison_tree():
    return Binary(
        Binary(
            Binary(
                Literal("alpha"),
                operator(TokenType.BANG_EQUAL, "!="),
                Literal("beta"),
            ),
            operator(TokenType.AND, "and"),
            Binary(
                Literal(10),
                operator(TokenType.GREATER_EQUAL, ">="),
                Literal(5),
            ),
        ),
        operator(TokenType.AND, "and"),
        Binary(
            Binary(
                Binary(
                    Literal(3),
                    operator(TokenType.LESS, "<"),
                    Literal(4),
                ),
                operator(TokenType.EQUAL_EQUAL, "=="),
                Literal(True),
            ),
            operator(TokenType.AND, "and"),
            Binary(
                Binary(
                    Literal(6),
                    operator(TokenType.GREATER, ">"),
                    Literal(2),
                ),
                operator(TokenType.EQUAL_EQUAL, "=="),
                Binary(
                    Literal(7),
                    operator(TokenType.LESS_EQUAL, "<="),
                    Literal(7),
                ),
            ),
        ),
    )


def logical_tree():
    return Binary(
        Binary(
            Literal(True),
            operator(TokenType.AND, "and"),
            Unary(operator(TokenType.BANG, "!"), Literal(False)),
        ),
        operator(TokenType.OR, "or"),
        Binary(
            Literal(None),
            operator(TokenType.EQUAL_EQUAL, "=="),
            Literal(None),
        ),
    )


EXAMPLES = (
    ("arithmetic", arithmetic_tree()),
    ("comparison", comparison_tree()),
    ("logical", logical_tree()),
)


def main():
    printer = AstPrinter()
    for name, expression in EXAMPLES:
        print(f"{name}: {printer.print(expression)}")


if __name__ == "__main__":
    main()
