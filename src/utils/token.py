from utils.token_type import TokenType


class Token:
    """
    Represents a token at a given line
    """

    def __init__(self, token_type: TokenType, lexeme: str, literal: object, line: int):
        """
        :param token_type: Type of token used
        :param lexeme: Raw substring of code e.g. "var", "language", "=", "lox", ";"
        :param literal: Number, string constant representation
        :param line: Line number
        """
        self.token_type: TokenType = token_type
        self.lexeme: str = lexeme
        self.literal: object = literal
        self.line: int = line

    def __str__(self) -> str:
        return f"{self.token_type} {self.lexeme} {self.literal}"

    def __repr__(self) -> str:
        return f"{self.token_type} {self.lexeme} {self.literal}"

    def __eq__(self, other) -> bool:
        return (
            self.token_type == other.token_type
            and self.lexeme == other.lexeme
            and self.literal == other.literal
            and self.line == other.line
        )
