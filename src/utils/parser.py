from typing import List

from utils.expr import Expr, Binary, Grouping, Literal, Unary, Variable, Assign, Logical, Call
from utils.stmt import Stmt, Print, Expression, Var, Block, If, While, Function, Return

from utils.token import Token
from utils.token_type import TokenType

from typing import Optional


class ParseError(Exception):
    pass


class Parser:
    """
    Parses a list of tokens after they have been scanned into statements following the grammar:

    program        -> declaration* EOF ;

    declaration    -> funDecl
                    | varDecl
                    | statement ;

    funDecl        -> "fun" function ;
    function       -> IDENTIFIER "(" parameters? ")" block ;
    parameters     -> IDENTIFIER ( "," IDENTIFIER )* ;

    varDecl        -> "var" IDENTIFIER ( "=" expression )? ";" ;

    statement      -> exprStmt
                    | forStmt
                    | ifStmt
                    | printStmt
                    | returnStmt
                    | whileStmt
                    | block ;

    returnStmt     -> "return" expression? ";" ;
    forStmt         -> "for" "(" ( varDecl | exprStmt | ";" )
                    expression? ";"
                    expression? ")" statement ;
    whileStmt      -> "while" "(" expression ")" statement ;
    block          -> "{" declaration* "}" ;
    exprStmt       -> expression ";"
    ifStmt         -> "if" "(" expression ")" statement
                    ( "else" statement )? ;
    printStmt      -> "print" expression ";" ;

    expression     -> assignment ;
    assignment     -> IDENTIFIER "=" assignment
                    | logic_or
    logic_or       -> logic_and ( "or" logic_and )* ;
    logic_and      -> equality ( "and" equality )* ;
    equality       -> comparison ( ( "!=" | "==" ) comparison )* ;
    comparison     -> term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
    term           -> factor ( ( "-" | "+" ) factor )* ;
    factor         -> unary ( ( "/" | "*" ) unary )* ;
    unary          -> ( "!" | "-" ) unary
                    | primary ;
    call           -> primary ( "(" arguments? ")" )* ;
    arguments      -> expression ( "," expression )* ;
    primary        -> NUMBER | STRING | "true" | "false" | "nil"
                    | "(" expression ")" ;
    """

    def __init__(self, pylox, tokens: List[Token]):
        """
        :param pylox: PyLox object
        :param tokens: List of tokens
        """
        self._pylox = pylox
        self._tokens: List[Token] = tokens
        self._current: int = 0

    def parse(self) -> Stmt:
        """
        program -> declaration* EOF
        """
        statements = []
        while not self._is_at_end():
            statements.append(self._declaration())

        return statements

    def _declaration(self) -> Optional[Stmt]:
        """
        declaration -> funDecl
                    | varDecl
                    | statement
        """
        try:
            if self._match([TokenType.VAR]):
                return self._var_declaration()
            if self._match([TokenType.FUN]):
                return self._function("function")
            return self._statement()

        except ParseError:
            self._synchronize()
            return None

    def _var_declaration(self) -> Var:
        """
        varDecl -> "var" IDENTIFIER ( "=" expression )? ";"
        """
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name")

        initializer = None
        if self._match([TokenType.EQUAL]):
            initializer = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration")
        return Var(name, initializer)

    def _statement(self) -> Stmt:
        """
        statement -> exprStmt
                    | forStmt
                    | ifStmt
                    | printStmt
                    | returnStmt
                    | whileStmt
                    | block
        """
        if self._match([TokenType.FOR]):
            return self._for_statement()

        if self._match([TokenType.IF]):
            return self._if_statement()

        if self._match([TokenType.PRINT]):
            return self._print_statement()

        if self._match([TokenType.RETURN]):
            return self._return_statement()

        if self._match([TokenType.WHILE]):
            return self._while_statement()

        if self._match([TokenType.LEFT_BRACE]):
            return Block(self._block())

        return self._expression_statement()

    def _return_statement(self) -> Return:
        """
        returnStmt -> "return" expression? ";"
        """
        keyword = self._previous()
        value = None
        if not self._check(TokenType.SEMICOLON):
            value = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after return value.")

        return Return(keyword, value)

    def _for_statement(self) -> Block:
        """
        forStmt -> "for" "(" ( varDecl | exprStmt | ";" )
                expression? ";"
                expression? ")" statement
        """
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'")
        if self._match([TokenType.SEMICOLON]):
            initializer = None
        elif self._match([TokenType.VAR]):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_statement()

        condition = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment = None
        if not self._check(TokenType.RIGHT_PAREN):
            increment = self._expression()

        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after 'clauses'")
        body = self._statement()

        if increment is not None:
            body = Block([body, Expression(increment)])

        # If condition is omitted, jam in true to make an infinite loop
        if condition is None:
            condition = Literal(True)

        body = While(condition, body)

        if initializer is not None:
            body = Block([initializer, body])

        return body

    def _if_statement(self) -> If:
        """
        ifStmt -> "if" "(" expression ")" statement
                ( "else" statement )?
        """
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition")

        then_branch = self._statement()
        else_branch = None

        if self._match([TokenType.ELSE]):
            else_branch = self._statement()

        return If(condition, then_branch, else_branch)

    def _while_statement(self) -> While:
        """
        whileStmt -> "while" "(" expression ")" statement
        """
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self._statement()

        return While(condition, body)

    def _block(self) -> List[Stmt]:
        """
        block -> "{" declaration* "}"
        """
        statements = []

        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            statements.append(self._declaration())

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after  block")
        return statements

    def _print_statement(self) -> Print:
        """
        printStmt -> "print" expression ";"
        """
        value = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value")
        return Print(value)

    def _expression_statement(self) -> Expression:
        """
        exprStmt -> expression ";"
        """
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after expression")
        return Expression(expr)

    def _function(self, kind: str) -> Function:
        name = self._consume(TokenType.IDENTIFIER, f"Expect {kind} name.")

        self._consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) > 255:
                    self._error(self._peek(), "Can't have more than 255 parameters.")

                parameters.append(self._consume(TokenType.IDENTIFIER, "Expect parameter name."))

                if not self._match([TokenType.COMMA]):
                    break
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self._consume(TokenType.LEFT_BRACE, "Expect '{' before {kind} body.")
        body = self._block()
        return Function(name, parameters, body)

    def _expression(self) -> Expr:
        """
        expression -> assignment
        """
        return self._assignment()

    def _assignment(self) -> Expr:
        """
        assignment -> IDENTIFIER "=" assignment
                    | logic_or
        """
        expr = self._or()

        if self._match([TokenType.EQUAL]):
            equals = self._previous()
            value = self._assignment()

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)

            self._error(equals, "Invalid assignment target")

        return expr

    def _or(self) -> Expr:
        """
        logic_or -> logic_and ( "or" logic_and )*
        """
        expr = self._and()

        while self._match([TokenType.OR]):
            operator = self._previous()
            right = self._and()
            expr = Logical(expr, operator, right)

        return expr

    def _and(self) -> Expr:
        """
        logic_and -> equality ( "and" equality )*
        """
        expr = self._equality()

        while self._match([TokenType.AND]):
            operator = self._previous()
            right = self._equality()
            expr = Logical(expr, operator, right)

        return expr

    def _equality(self) -> Expr:
        """
        equality -> comparison ( ( "!=" | "==" ) comparison )*
        """
        expr = self._comparison()

        while self._match([TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL]):
            operator = self._previous()
            right = self._comparison()
            expr = Binary(expr, operator, right)

        return expr

    def _comparison(self) -> Expr:
        """
        comparison -> term ( ( ">" | ">=" | "<" | "<=" ) term )*
        """
        expr = self._term()

        while self._match([TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS_EQUAL, TokenType.LESS]):
            operator = self._previous()
            right = self._term()
            expr = Binary(expr, operator, right)

        return expr

    def _term(self) -> Expr:
        """
        term -> factor ( ( "-" | "+" ) factor )*
        """
        expr = self._factor()

        while self._match([TokenType.MINUS, TokenType.PLUS]):
            operator = self._previous()
            right = self._factor()
            expr = Binary(expr, operator, right)

        return expr

    def _factor(self) -> Expr:
        """
        unary ( ( "/" | "*" ) unary )*
        """
        expr = self._unary()

        while self._match([TokenType.SLASH, TokenType.STAR]):
            operator = self._previous()
            right = self._unary()
            expr = Binary(expr, operator, right)

        return expr

    def _unary(self) -> Expr:
        """
        unary -> ( "!" | "-" ) unary | primary
        """
        if self._match([TokenType.BANG, TokenType.MINUS]):
            operator = self._previous()
            right = self._unary()
            return Unary(operator, right)

        return self._call()

    def _call(self) -> Expr:
        """
        call -> primary ( "(" arguments? ")" )*
        """
        expr = self._primary()

        while True:
            if self._match([TokenType.LEFT_PAREN]):
                expr = self._finish_call(expr)
            else:
                break

        return expr

    def _finish_call(self, callee: Expr) -> Call:
        """
        Parse the call expression using the previously parsed expression as callee
        """
        arguments = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self._error(self._peek(), "Can't have more than 255 arguments.")
                arguments.append(self._expression())
                if not self._match([TokenType.COMMA]):
                    break

        paren = self._consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")

        return Call(callee, paren, arguments)

    def _primary(self) -> Expr:
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

    def _match(self, types: List[Token]) -> bool:
        """
        Check if current token is any of the given types
        """
        for t in types:
            if self._check(t):
                self._advance()
                return True
        return False

    def _check(self, token_type: TokenType) -> bool:
        """
        True if curent token is of the given type
        """
        if self._is_at_end():
            return False
        return self._peek().token_type == token_type

    def _advance(self) -> Token:
        """
        Consume current token and return it
        """
        if not self._is_at_end():
            self._current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        """
        Check if we're out of tokens to parse
        """
        return self._peek().token_type == TokenType.EOF

    def _peek(self) -> Token:
        """
        Return current token
        """
        return self._tokens[self._current]

    def _previous(self) -> Token:
        """
        Return previous token
        """
        return self._tokens[self._current - 1]

    def _consume(self, token_type: TokenType, message: str) -> Token:
        """
        Check if next token is expected, if so consume, else we've hit an error
        """
        if self._check(token_type):
            return self._advance()

        raise self._error(self._peek(), message)

    def _error(self, token_type: TokenType, message: str) -> ParseError:
        self._pylox.error_token(token_type, message)
        return ParseError(message)

    def _synchronize(self) -> None:
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
