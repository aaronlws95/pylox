from utils.token_type import TokenType


class Token:
    """
    Represents a token at a given line
    """

    def __init__(self, token_type: TokenType, lexeme: str, literal: object, line: int):
        self.token_type: TokenType = token_type
        self.lexeme: str = lexeme
        self.literal: object = literal
        self.line: int = line

    def __str__(self):
        return f"{self.token_type} {self.lexeme} {self.literal}"

    def __repr__(self):
        return f"{self.token_type} {self.lexeme} {self.literal}"

    def __eq__(self, other):
        return (
            self.token_type == other.token_type
            and self.lexeme == other.lexeme
            and self.literal == other.literal
            and self.line == other.line
        )
