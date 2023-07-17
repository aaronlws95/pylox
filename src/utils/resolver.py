from enum import Enum
from utils.expr import Expr, Binary, Grouping, Literal, Unary, Variable, Assign, Logical, Call
from utils.stmt import Stmt, Print, Expression, Var, Block, If, While, Function, Return
from utils.token import Token
from typing import List, Union


class FunctionType(Enum):
    NONE = 0
    FUNCTION = 1


class Resolver(Expr.Visitor, Stmt.Visitor):
    def __init__(self, pylox, interpreter):
        self._pylox = pylox
        self._interpreter = interpreter
        self._scopes = []  # stack: back [outer_scope, ..., inner_scope] front
        self._current_function = FunctionType.NONE

    def visit_block_stmt(self, stmt: Block) -> None:
        self._begin_scope()
        self.resolve(stmt.statements)
        self._end_scope()

    def visit_function_stmt(self, stmt: Function) -> None:
        self._declare(stmt.name)
        self._define(stmt.name)

        self._resolve_function(stmt, FunctionType.FUNCTION)

    def visit_var_stmt(self, stmt: Var) -> None:
        self._declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        self._define(stmt.name)

    def visit_expression_stmt(self, stmt: Expression) -> None:
        self.resolve(stmt.expression)

    def visit_if_stmt(self, stmt: If) -> None:
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)

        if stmt.else_branch is not None:
            self.resolve(stmt.else_branch)

    def visit_print_stmt(self, stmt: Print) -> None:
        self.resolve(stmt.expression)

    def visit_return_stmt(self, stmt: Return) -> None:
        if self._current_function == FunctionType.NONE:
            self._pylox.error_token(stmt.keyword, "Can't return from top-level code.")

        if stmt.value is not None:
            self.resolve(stmt.value)

    def visit_while_stmt(self, stmt: While) -> None:
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    def visit_binary_expr(self, expr: Binary) -> None:
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_call_expr(self, expr: Call) -> None:
        self.resolve(expr.callee)

        for argument in expr.arguments:
            self.resolve(argument)

    def visit_grouping_expr(self, expr: Grouping) -> None:
        self.resolve(expr.expression)

    def visit_literal_expr(self, expr: Literal) -> None:
        return None

    def visit_logical_expr(self, expr: Logical) -> None:
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_unary_expr(self, expr: Unary) -> None:
        self.resolve(expr.right)

    def visit_variable_expr(self, expr: Variable) -> None:
        if self._scopes:
            if expr.name.lexeme in self._scopes[-1] and not self._scopes[-1][expr.name.lexeme]:
                self._pylox.error_token(expr.name, "Can't read local variable in its own initializer.")

        self._resolve_local(expr, expr.name)

    def visit_assign_expr(self, expr: Assign) -> None:
        self.resolve(expr.value)
        self._resolve_local(expr, expr.name)

    def _declare(self, name: Token) -> None:
        """
        Add variable to the innermost scope so that it shadows any
        outer one and so that we know the variable exists. It is marked as
        "not ready yet" by binding its name to false in the scope map.
        """
        if not self._scopes:
            return

        peek = self._scopes[-1]

        if name.lexeme in peek:
            self._pylox.error_token(name, "Already a variable with this name in this scope.")

        peek.update({name.lexeme: False})

    def _define(self, name: Token) -> None:
        """
        After declaring and resolving, the variable is ready and set to true
        to mark it as fully initialized and available for use
        """
        if not self._scopes:
            return

        self._scopes[-1].update({name.lexeme: True})

    def _begin_scope(self) -> None:
        self._scopes.append({})

    def _end_scope(self) -> None:
        self._scopes.pop()

    def _resolve_function(self, function: Function, function_type: FunctionType) -> None:
        enclosing_function = self._current_function
        self._current_function = function_type

        self._begin_scope()
        for param in function.params:
            self._declare(param)
            self._define(param)

        self.resolve(function.body)
        self._end_scope()
        self._current_function = enclosing_function

    def _resolve_local(self, expr: Expr, name: Token) -> None:
        for i in reversed(range(len(self._scopes))):
            if name.lexeme in self._scopes[i]:
                self._interpreter.resolve(expr, len(self._scopes) - 1 - i)
                return

    def resolve(self, target: Union[Expr, Stmt, List[Stmt]]) -> None:
        if isinstance(target, list):
            for x in target:
                self.resolve(x)
        else:
            target.accept(self)
