try:
    from .expr import Binary, Grouping, Literal, Unary
    from .token_type import TokenType
except ImportError:  # running from src/main.py
    from expr import Binary, Grouping, Literal, Unary
    from token_type import TokenType


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.errors = []

    def parse(self):
        try:
            expression = self.expression()

            # one expression only for this lab
            if not self.is_at_end():
                raise self.error(
                    self.peek(),
                    "Unexpected token after expression.",
                )

            return expression
        except ParseError:
            return None

    def expression(self):
        return self.logic_or()

    # one method per precedence level
    def logic_or(self):
        expression = self.logic_and()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logic_and()
            expression = Binary(expression, operator, right)

        return expression

    def logic_and(self):
        expression = self.equality()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expression = Binary(expression, operator, right)

        return expression

    def equality(self):
        expression = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expression = Binary(expression, operator, right)

        return expression

    def comparison(self):
        expression = self.term()

        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self.previous()
            right = self.term()
            expression = Binary(expression, operator, right)

        return expression

    def term(self):
        expression = self.factor()

        # loop makes these operators lean left
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expression = Binary(expression, operator, right)

        return expression

    def factor(self):
        expression = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expression = Binary(expression, operator, right)

        return expression

    def unary(self):
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            # calls itself so !!false works too
            right = self.unary()
            return Unary(operator, right)

        return self.primary()

    def primary(self):
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NULL):
            return Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)

        if self.match(TokenType.LEFT_PAREN):
            # parentheses can contain the whole grammar again
            expression = self.expression()
            self.consume(
                TokenType.RIGHT_PAREN,
                "Expected ')' after expression.",
            )
            return Grouping(expression)

        raise self.error(self.peek(), "Expected expression.")

    def match(self, *types):
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def consume(self, token_type, message):
        if self.check(token_type):
            return self.advance()
        raise self.error(self.peek(), message)

    def check(self, token_type):
        if self.is_at_end():
            return token_type == TokenType.EOF
        return self.peek().type == token_type

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def error(self, token, message):
        location = "at end" if token.type == TokenType.EOF else f"at {token.lexeme!r}"
        self.errors.append((token.line, location, message))
        return ParseError()
