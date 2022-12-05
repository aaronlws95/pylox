from typing import List

from utils.expr import Binary, Grouping, Literal, Unary
from utils.token import Token
from utils.token_type import TokenType


class ParseError(Exception):
    pass


class Parser:
    """
    Parses a list of tokens into expressions
    """
    def __init__(self, pylox, tokens):
        self._pylox = pylox
        self._tokens: List[Token] = tokens
        self._current: int = 0

    def _expression(self):
        """
        expression -> equality
        """
        return self._equality()

    def _equality(self):
        """
        equality -> comparison ( ( "!=" | "==" ) comparison )*
        """
        expr = self._comparison()

        while self._match([TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL]):
            operator = self._previous()
            right = self._comparison()
            expr = Binary(expr, operator, right)

        return expr

    def _comparison(self):
        """
        comparison -> term ( ( ">" | ">=" | "<" | "<=" ) term )*
        """
        expr = self._term()

        while self._match([TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS_EQUAL, TokenType.LESS]):
            operator = self._previous()
            right = self._term()
            expr = Binary(expr, operator, right)

        return expr

    def _term(self):
        """
        term -> factor ( ( "-" | "+" ) factor )*
        """
        expr = self._factor()

        while self._match([TokenType.MINUS, TokenType.PLUS]):
            operator = self._previous()
            right = self._factor()
            expr = Binary(expr, operator, right)

        return expr

    def _factor(self):
        """
        unary ( ( "/" | "*" ) unary )*
        """
        expr = self._unary()

        while self._match([TokenType.SLASH, TokenType.STAR]):
            operator = self._previous()
            right = self._unary()
            expr = Binary(expr, operator, right)

        return expr

    def _unary(self):
        """
        unary -> ( "!" | "-" ) unary | primary
        """
        if self._match([TokenType.BANG, TokenType.MINUS]):
            operator = self._previous()
            right = self._unary()
            return Unary(operator, right)

        return self._primary()

    def _primary(self):
        """
        primary -> NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")"
        """
        if self._match([TokenType.FALSE]):
            return Literal(False)

        if self._match([TokenType.TRUE]):
            return Literal(True)

        if self._match([TokenType.NIL]):
            return Literal(None)

        if self._match([TokenType.NUMBER, TokenType.STRING]):
            return Literal(self._previous().literal)

        if self._match([TokenType.LEFT_PAREN]):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        raise self._error(self._peek(), "Expect expression.")

    def _match(self, types: List[Token]):
        """
        Check if current token is any of the given types
        """
        for t in types:
            if self._check(t):
                self._advance()
                return True
        return False

    def _check(self, token_type: TokenType):
        """
        True if curent token is of the given type
        """
        if self._is_at_end():
            return False
        return self._peek().token_type == token_type

    def _advance(self):
        """
        Consume current token and return it
        """
        if not self._is_at_end():
            self._current += 1
        return self._previous()

    def _is_at_end(self):
        """
        Check if we're out of tokens to parse
        """
        return self._peek().token_type == TokenType.EOF

    def _peek(self):
        """
        Return current token
        """
        return self._tokens[self._current]

    def _previous(self):
        """
        Return previous token
        """
        return self._tokens[self._current - 1]

    def _consume(self, token_type, message):
        """
        Check if next token is expected, if so consume, else we've hit an error
        """
        if self._check(token_type):
            return self._advance()

        raise self._error(self._peek(), message)

    def _error(self, token_type, message):
        self._pylox.error_token(token_type, message)
        return ParseError(message)

    def _synchronize(self):
        self._advance()

        while not self._is_at_end():
            if self._previous().token_type == TokenType.SEMICOLON:
                return

            if self._peek() in [
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            ]:
                return

        self._advance()

    def parse(self):
        try:
            return self._expression()
        except ParseError:
            return None
    