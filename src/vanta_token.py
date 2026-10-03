class Token:
    def __init__(self, token_type, lexeme, literal, line):
        self.type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self) -> str:
        return (
            f"{self.type.name:<14} "
            f"lexeme={self.lexeme!r} literal={self.literal!r} line={self.line}"
        )
