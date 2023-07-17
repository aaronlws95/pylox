from typing import Any, List

from utils.environment import Environment
from utils.expr import (
    Assign,
    Binary,
    Call,
    Expr,
    Get,
    Grouping,
    Literal,
    Logical,
    Set,
    Unary,
    This,
    Variable,
)
from utils.lox_callable import LoxCallable
from utils.lox_function import LoxFunction
from utils.lox_instance import LoxInstance
from utils.lox_native import Clock
from utils.return_exception import ReturnException
from utils.runtime_error import PyLoxRuntimeError
from utils.stmt import Block, Expression, Function, If, Print, Return, Stmt, Var, While, Class
from utils.token import Token
from utils.token_type import TokenType
from utils.lox_class import LoxClass


class Interpreter(Expr.Visitor, Stmt.Visitor):
    """
    Executes PyLox statements after they have been parsed by the parser
    """

    def __init__(self):
        self.globals = Environment()  # Fixed reference to the outermost environment
        self._environment = self.globals  # Changes as we enter and exit local scopes
        self._locals = {}  # Resolution information

        # Define native functions
        self._environment.define("clock", Clock())

    def interpret(self, pylox, statements: List[Stmt]) -> None:
        try:
            for statement in statements:
                self._execute(statement)

        except PyLoxRuntimeError as error:
            pylox.runtime_error(error)

    def _execute(self, stmt: Stmt) -> None:
        stmt.accept(self)

    def resolve(self, expr: Expr, depth: int) -> None:
        self._locals.update({expr: depth})

    def _execute_block(self, statements: List[Stmt], environment: Environment) -> None:
        previous = self._environment

        try:
            self._environment = environment  # Set environment to enclosing

            for statement in statements:
                self._execute(statement)
        # Don't except Exceptions here as it would override ReturnException
        finally:
            self._environment = previous

    def _stringify(self, obj: object) -> str:
        if obj is None:
            return "nil"

        if isinstance(obj, float):
            text = str(obj)
            if text[-2:] == ".0":
                text = text[:-2]

            return text

        return str(obj)

    def _checkNumberOperand(self, operator: Token, operand: object) -> None:
        if isinstance(operand, float):
            return
        raise PyLoxRuntimeError(operator, "Operand must be a number")

    def _checkNumberOperands(self, operator: Token, left: object, right: object) -> None:
        if isinstance(left, float) and isinstance(right, float):
            return None
        raise PyLoxRuntimeError(operator, "Operands must be numbers")

    def _is_equal(self, a: object, b: object) -> bool:
        if a is None and b is None:
            return True

        if a is None:
            return False

        return a == b

    def _is_truthy(self, obj: object) -> bool:
        """
        Check if object is "truthy". None and false are falsey, everything else is truthy.
        """
        if obj is None:
            return False

        if isinstance(obj, bool):
            return bool(obj)

        return True

    def _evaluate(self, expr) -> Any:
        return expr.accept(self)

    def _lookup_variable(self, name: Token, expr: Expr) -> object:
        if expr in self._locals:
            distance = self._locals[expr]
            return self._environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)

    def visit_assign_expr(self, expr: Assign) -> Any:
        value = self._evaluate(expr.value)

        if expr in self._locals:
            distance = self._locals[expr]
            self._environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)
        return value

    def visit_block_stmt(self, stmt: Block) -> None:
        self._execute_block(stmt.statements, Environment(self._environment))

    def visit_class_stmt(self, stmt: Class) -> None:
        self._environment.define(stmt.name.lexeme, None)

        methods = {}
        for method in stmt.methods:
            function = LoxFunction(method, self._environment, method.name.lexeme == "init")
            methods[method.name.lexeme] = function

        klass = LoxClass(stmt.name.lexeme, methods)
        self._environment.assign(stmt.name, klass)

    def visit_expression_stmt(self, stmt: Expression) -> None:
        self._evaluate(stmt.expression)

    def visit_function_stmt(self, stmt: Function) -> None:
        function = LoxFunction(stmt, self._environment, False)
        self._environment.define(stmt.name.lexeme, function)

    def visit_if_stmt(self, stmt: If) -> None:
        if self._is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self._execute(stmt.else_branch)

    def visit_print_stmt(self, stmt: Print) -> None:
        value = self._evaluate(stmt.expression)
        print(self._stringify(value))

    def visit_return_stmt(self, stmt: Return) -> None:
        value = None
        if stmt.value is not None:
            value = self._evaluate(stmt.value)

        raise ReturnException(value)

    def visit_var_stmt(self, stmt: Var) -> None:
        value = None
        if stmt.initializer is not None:
            value = self._evaluate(stmt.initializer)

        self._environment.define(stmt.name.lexeme, value)

    def visit_while_stmt(self, stmt: While) -> None:
        while self._is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.body)

    def visit_call_expr(self, expr: Call) -> Expr:
        callee = self._evaluate(expr.callee)

        arguments = []
        for argument in expr.arguments:
            arguments.append(self._evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise RuntimeError(expr.paren, "Can only call functions and classes.")

        function: LoxCallable = callee

        if len(arguments) != function.arity():
            raise RuntimeError(expr.paren, f"Expected {function.arity()} arguments but got {len(arguments)}.")

        return function.call(self, arguments)

    def visit_literal_expr(self, expr: Literal) -> object:
        return expr.value

    def visit_logical_expr(self, expr: Logical) -> Expr:
        left = self._evaluate(expr.left)

        # Evaluate left first to see if we can short-circuit
        if expr.operator.token_type == TokenType.OR:
            if self._is_truthy(left):
                return left
        else:  # AND
            if not self._is_truthy(left):
                return left

        return self._evaluate(expr.right)

    def visit_set_expr(self, expr: Set) -> object:
        obj = self._evaluate(expr.obj)

        if not isinstance(obj, LoxInstance):
            raise RuntimeError(expr.name, "Only instances have fields.")

        value = self._evaluate(expr.value)
        obj.sett(expr.name, value)
        return value

    def visit_this_expr(self, expr: This) -> object:
        return self._lookup_variable(expr.keyword, expr)

    def visit_get_expr(self, expr: Get) -> object:
        obj = self._evaluate(expr.obj)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)

        raise RuntimeError(expr.name, "Only instances have properties.")

    def visit_grouping_expr(self, expr: Grouping) -> Expr:
        return self._evaluate(expr.expression)

    def visit_unary_expr(self, expr: Unary) -> Any:
        right = self._evaluate(expr.right)

        if expr.operator.token_type == TokenType.MINUS:
            self._checkNumberOperand(expr.operator, right)
            return -float(right)
        elif expr.operator.token_type == TokenType.BANG:
            return self._is_truthy(right)

    def visit_variable_expr(self, expr: Variable) -> object:
        return self._lookup_variable(expr.name, expr)

    def visit_binary_expr(self, expr: Binary) -> Any:  # noqa C901
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)

        if expr.operator.token_type == TokenType.MINUS:
            self._checkNumberOperands(expr.operator, left, right)
            return float(left) - float(right)
        if expr.operator.token_type == TokenType.SLASH:
            self._checkNumberOperands(expr.operator, left, right)
            return left / right
        if expr.operator.token_type == TokenType.STAR:
            self._checkNumberOperands(expr.operator, left, right)
            return left * right
        if expr.operator.token_type == TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return float(left) + float(right)

            if isinstance(left, str) and isinstance(right, str):
                return str(left) + str(right)

            raise PyLoxRuntimeError(expr.operator, "Operands must be two numbers or two strings")

        if expr.operator.token_type == TokenType.GREATER:
            self._checkNumberOperands(expr.operator, left, right)
            return left > right
        if expr.operator.token_type == TokenType.GREATER_EQUAL:
            self._checkNumberOperands(expr.operator, left, right)
            return left >= right
        if expr.operator.token_type == TokenType.LESS:
            self._checkNumberOperands(expr.operator, left, right)
            return left < right
        if expr.operator.token_type == TokenType.LESS_EQUAL:
            self._checkNumberOperands(expr.operator, left, right)
            return left <= right

        if expr.operator.token_type == TokenType.BANG_EQUAL:
            return not self._is_equal(left, right)
        if expr.operator.token_type == TokenType.EQUAL_EQUAL:
            return self._is_equal(left, right)
