from typing import Any, List

from utils.token import Token
from utils.token_type import TokenType


class Scanner:
    """
    Scans the source code and fills a list of tokens ending with EOF
    """

    def __init__(self, pylox, source: str):
        """
        :param pylox: PyLox object
        :param source: Source code to scan
        """
        self._pylox = pylox
        self._source: str = source
        self._tokens: List[TokenType] = []
        self._start: int = 0
        self._current: int = 0
        self._line: int = 1
        self._nested_comment_depth: int = 0

    def scan_tokens(self) -> List[TokenType]:
        """
        Scan and fill list with tokens
        """
        while not self._is_at_end():
            self._start = self._current
            self._scan_token()

        self._tokens.append(Token(TokenType.EOF, "", None, self._line))
        return self._tokens

    def _scan_token(self) -> None:  # noqa C901
        """
        Get next token
        """
        c = self._advance()
        if c in TokenType._value2member_map_:
            # // Single-line comment
            if c == "/" and self._match("/"):
                while self._peek() != "\n" and not self._is_at_end():
                    self._advance()
            # Start multi-line comment
            elif c == "/" and self._match("*"):
                self._nested_comment_depth += 1
                while (
                    not (self._peek() == "*" and self._peek_next() == "/")
                    and not (self._peek() == "/" and self._peek_next() == "*")
                    and not self._is_at_end()
                ):
                    cur = self._advance()
                    if cur == "\n":
                        self._line += 1
            # End multi-line comment
            elif c == "*" and self._match("/"):
                self._nested_comment_depth -= 1
            # Two character tokens
            elif self._match("=") and c + "=" in TokenType._value2member_map_:
                self._add_token(TokenType(c + "="))
            # Single character tokens
            else:
                self._add_token(TokenType(c))
        # Continue multi-line comment if nested
        elif self._nested_comment_depth > 0:
            while (
                not (self._peek() == "*" and self._peek_next() == "/")
                and not (self._peek() == "/" and self._peek_next() == "*")
                and not self._is_at_end()
            ):
                cur = self._advance()
                if cur == "\n":
                    self._line += 1
        # New line
        elif c == "\n":
            self._line += 1
        # String literal
        elif c == '"':
            self._add_string()
        # Number literal
        elif Scanner._is_digit(c):
            self._add_number()
        # Identifier
        elif Scanner._is_alpha(c):
            self._add_identifier()
        # Empty space
        elif c == " " or c == "\t" or c == "\r":
            pass
        else:
            self._pylox.error_line(self._line, f"Unexpected character: {c}")

    def _is_at_end(self) -> bool:
        """
        Check if we have reached the end of the source code
        """
        return self._current >= len(self._source)

    def _add_string(self) -> None:
        """
        Add string to tokens
        """
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == "\n":
                self._line += 1
            self._advance()

        if self._is_at_end():
            self._pylox.error_line(self._line, "Unterminated string")
            return

        # Closing "
        self._advance()

        value = self._source[self._start + 1 : self._current - 1]
        self._add_token(TokenType.STRING, value)

    def _add_number(self) -> None:
        """
        Add number to tokens
        """
        while Scanner._is_digit(self._peek()):
            self._advance()

        if self._peek() == "." and Scanner._is_digit(self._peek_next()):
            self._advance()
            while Scanner._is_digit(self._peek()):
                self._advance()

        self._add_token(TokenType.NUMBER, float(self._source[self._start : self._current]))

    def _add_identifier(self) -> None:
        """
        Add keyword if current lexeme matches keyword otherwise add identifier to tokens
        """

        while Scanner._is_alphanumeric((self._peek())):
            self._advance()

        text = self._source[self._start : self._current]

        token_type = None
        if text in TokenType._value2member_map_:
            token_type = TokenType(text)

        if token_type is None:
            token_type = TokenType.IDENTIFIER

        self._add_token(token_type)

    def _peek(self) -> str:
        """
        Get current character in source
        """
        if self._is_at_end():
            return "\0"
        return self._source[self._current]

    def _peek_next(self) -> str:
        """
        Get next character in source
        """
        if self._current + 1 >= len(self._source):
            return "\0"

        return self._source[self._current + 1]

    def _match(self, expected: str) -> bool:
        """
        Check if current character matches with expected
        """
        if self._is_at_end():
            return False
        if self._source[self._current] != expected:
            return False

        self._current += 1
        return True

    def _advance(self) -> str:
        """
        Get next character in source
        """
        c = self._source[self._current]
        self._current += 1
        return c

    def _add_token(self, token_type: TokenType, literal: Any = None) -> None:
        """
        Append token to list
        """
        text = self._source[self._start : self._current]
        self._tokens.append(Token(token_type, text, literal, self._line))

    @staticmethod
    def _is_digit(c: str) -> bool:
        """
        Check if c is a digit 0...9
        """
        return c >= "0" and c <= "9"

    @staticmethod
    def _is_alpha(c: str) -> bool:
        """
        Check if c is an alphabet or underscore
        """
        return (c >= "a" and c <= "z") or (c >= "A" and c <= "Z") or c == "_"

    @staticmethod
    def _is_alphanumeric(c: str) -> bool:
        """
        Check if c is an alphabet, underscore, or a digit
        """
        return Scanner._is_alpha(c) or Scanner._is_digit(c)
