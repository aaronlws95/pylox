from typing import List

from utils.expr import Binary, Grouping, Literal, Unary, Variable, Assign
from utils.token import Token
from utils.token_type import TokenType
from utils.stmt import Print, Expression, Var, Block


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

    def parse(self):
        statements = []
        while not self._is_at_end():
            statements.append(self._declaration())

        return statements

    def _declaration(self):
        try:
            if self._match([TokenType.VAR]):
                return self._var_declaration()
            return self._statements()

        except ParseError:
            self._synchronize()
            return None

    def _var_declaration(self):
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name")

        initializer = None
        if self._match([TokenType.EQUAL]):
            initializer = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration")
        return Var(name, initializer)

    def _statements(self):
        if self._match([TokenType.PRINT]):
            return self._print_statement()

        if self._match([TokenType.LEFT_BRACE]):
            return Block(self._block())

        return self._expression_statement()

    def _block(self):
        statements = []

        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            statements.append(self._declaration())

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after  block")
        return statements

    def _print_statement(self):
        value = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value")
        return Print(value)

    def _expression_statement(self):
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after expression")
        return Expression(expr)

    def _assignment(self):
        expr = self._equality()

        if self._match([TokenType.EQUAL]):
            equals = self._previous()
            value = self._assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)

            self._error(equals, "Invalid assignment target")

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

        if self._match([TokenType.IDENTIFIER]):
            return Variable(self._previous())

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
        """
        Align state such that next token matches the rule being parsed
        """
        self._advance()

        while not self._is_at_end():
            if self._previous().token_type == TokenType.SEMICOLON:
                return

            if self._peek().token_type in [
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
