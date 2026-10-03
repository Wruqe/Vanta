try:
    from .token_type import TokenType
    from .vanta_token import Token
except ImportError:  # Support running src/main.py directly.
    from token_type import TokenType
    from vanta_token import Token


class Scanner:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.errors = []

        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self):
        while not self.is_at_end():
            # new token starts wherever we left off
            self.start = self.current
            self.scan_token()

        # always one of these at the end
        self.tokens.append(
            Token(TokenType.EOF, "", None, self.line)
        )

        return self.tokens

    def scan_token(self):
        c = self.advance()

        if c == "(":
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ")":
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == "{":
            self.add_token(TokenType.LEFT_BRACE)
        elif c == "}":
            self.add_token(TokenType.RIGHT_BRACE)
        elif c == ",":
            self.add_token(TokenType.COMMA)
        elif c == ".":
            self.add_token(TokenType.DOT)
        elif c == "-":
            self.add_token(TokenType.MINUS)
        elif c == "+":
            self.add_token(TokenType.PLUS)
        elif c == ";":
            self.add_token(TokenType.SEMICOLON)
        elif c == "*":
            self.add_token(TokenType.STAR)
        elif c == "!":
            self.add_token(TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG)
        elif c == "=":
            self.add_token(TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL)
        elif c == "<":
            self.add_token(TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS)
        elif c == ">":
            self.add_token(TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER)
        elif c == "/":
            # comment, or just regular division
            if self.match("/"):
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)
        elif c in (" ", "\r", "\t"):
            pass
        elif c == "\n":
            self.line += 1
        elif c == '"':
            self.string()
        elif self.is_digit(c):
            self.number()
        elif self.is_alpha(c):
            self.identifier()
        else:
            self.error(f"Unexpected character {c!r}.")

    def advance(self):
        character = self.source[self.current]
        self.current += 1
        return character

    def match(self, expected):
        if self.is_at_end() or self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self):
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def add_token(self, token_type, literal=None):
        text = self.source[self.start:self.current]

        self.tokens.append(
            Token(token_type, text, literal, self.line)
        )

    def string(self):
        value = []

        while not self.is_at_end():
            character = self.advance()

            if character == '"':
                self.add_token(TokenType.STRING, "".join(value))
                return

            if character == "\n":
                self.line += 1
                value.append(character)
                continue

            if character == "\\" and not self.is_at_end():
                escaped = self.advance()
                replacement = ESCAPE_SEQUENCES.get(escaped)
                if replacement is None:
                    self.error(f"Invalid escape sequence '\\{escaped}'.")
                    value.append(escaped)
                else:
                    value.append(replacement)
                continue

            value.append(character)

        self.error("Unterminated string.")

    def number(self):
        while self.is_digit(self.peek()):
            self.advance()

        # dot only counts when another digit follows
        if self.peek() == "." and self.is_digit(self.peek_next()):
            self.advance()
            while self.is_digit(self.peek()):
                self.advance()

        text = self.source[self.start:self.current]
        literal = float(text) if "." in text else int(text)
        self.add_token(TokenType.NUMBER, literal)

    def identifier(self):
        # grab the whole word, then see if it is special
        while self.is_alpha_numeric(self.peek()):
            self.advance()

        text = self.source[self.start:self.current]
        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)
        literal = KEYWORD_LITERALS.get(token_type)
        self.add_token(token_type, literal)

    def error(self, message):
        # save it and let the scanner keep moving
        self.errors.append((self.line, message))

    @staticmethod
    def is_digit(character):
        return "0" <= character <= "9"

    @staticmethod
    def is_alpha(character):
        return (
            "a" <= character <= "z"
            or "A" <= character <= "Z"
            or character == "_"
        )

    @classmethod
    def is_alpha_numeric(cls, character):
        return cls.is_alpha(character) or cls.is_digit(character)

    def is_at_end(self):
        return self.current >= len(self.source)


KEYWORDS = {
    "and": TokenType.AND,
    "let": TokenType.LET,
    "fn": TokenType.FN,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "return": TokenType.RETURN,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "null": TokenType.NULL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
}

KEYWORD_LITERALS = {
    TokenType.TRUE: True,
    TokenType.FALSE: False,
    TokenType.NULL: None,
}

ESCAPE_SEQUENCES = {
    '"': '"',
    "\\": "\\",
    "n": "\n",
    "r": "\r",
    "t": "\t",
}
