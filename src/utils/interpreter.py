from typing import List
from utils.expr import Expr
from utils.token import Token
from utils.token_type import TokenType
from utils.runtime_error import PyLoxRuntimeError
from utils.stmt import Stmt
from utils.environment import Environment


class Interpreter(Expr.Visitor, Stmt.Visitor):
    def __init__(self):
        self._environment = Environment()

    def interpret(self, pylox, statements: List[Stmt]):
        try:
            for statement in statements:
                self._execute(statement)

        except PyLoxRuntimeError as error:
            pylox.runtime_error(error)

    def _execute(self, stmt):
        stmt.accept(self)

    def _stringify(self, obj):
        if obj is None:
            return "nil"

        if isinstance(obj, float):
            text = str(obj)
            if text[-2:] == ".0":
                text = text[:-2]

            return text

        return str(obj)

    def visit_assign_expr(self, expr):
        value = self._evaluate(expr.value)
        self._environment.assign(expr.name, value)
        return value

    def visit_block_stmt(self, stmt):
        self._execute_block(stmt.statements, Environment(self._environment))
        return None

    def _execute_block(self, statements, environment):
        previous = self._environment

        try:
            self._environment = environment

            for statement in statements:
                self._execute(statement)
        except Exception:
            pass

        self._environment = previous

    def visit_expression_stmt(self, stmt):
        self._evaluate(stmt.expression)
        return None

    def visit_print_stmt(self, stmt):
        value = self._evaluate(stmt.expression)
        print(self._stringify(value))
        return None

    def visit_var_stmt(self, stmt):
        value = None
        if stmt.initializer is not None:
            value = self._evaluate(stmt.initializer)

        self._environment.define(stmt.name.lexeme, value)

    def visit_literal_expr(self, expr):
        return expr.value

    def visit_grouping_expr(self, expr):
        return self._evaluate(expr.expression)

    def visit_unary_expr(self, expr):
        right = self._evaluate(expr.right)

        if expr.operator.token_type == TokenType.MINUS:
            self._checkNumberOperand(expr.operator, right)
            return -float(right)
        elif expr.operator.token_type == TokenType.BANG:
            return self._is_truthy(right)

        return None

    def visit_variable_expr(self, expr):
        return self._environment.get(expr.name)

    def _checkNumberOperand(self, operator: Token, operand: object):
        if isinstance(operand, float):
            return
        raise PyLoxRuntimeError(operator, "Operand must be a number")

    def _checkNumberOperands(self, operator: Token, left: object, right: object):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise PyLoxRuntimeError(operator, "Operands must be numbers")

    def visit_binary_expr(self, expr):
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)

        if expr.operator.token_type == TokenType.MINUS:
            self._checkNumberOperand(expr.operator, left, right)
            return float(left) - float(right)
        if expr.operator.token_type == TokenType.SLASH:
            self._checkNumberOperand(expr.operator, left, right)
            return left / right
        if expr.operator.token_type == TokenType.STAR:
            self._checkNumberOperand(expr.operator, left, right)
            return left * right
        if expr.operator.token_type == TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return float(left) + float(right)

            if isinstance(left, str) and isinstance(right, str):
                return str(left) + str(right)

            raise PyLoxRuntimeError(expr.operator, "Operands must be two numbers or two strings")

        if expr.operator.token_type == TokenType.GREATER:
            self._checkNumberOperand(expr.operator, left, right)
            return left > right
        if expr.operator.token_type == TokenType.GREATER_EQUAL:
            self._checkNumberOperand(expr.operator, left, right)
            return left >= right
        if expr.operator.token_type == TokenType.LESS:
            self._checkNumberOperand(expr.operator, left, right)
            return left < right
        if expr.operator.token_type == TokenType.LESS_EQUAL:
            self._checkNumberOperand(expr.operator, left, right)
            return left <= right

        if expr.operator.token_type == TokenType.BANG_EQUAL:
            return not self._is_equal(left, right)
        if expr.operator.token_type == TokenType.EQUAL_EQUAL:
            return self._is_equal(left, right)

        return None

    def _is_equal(self, a, b):
        if a is None and b is None:
            return True

        if a is None:
            return False

        return a == b

    def _is_truthy(self, obj):
        """
        Check if object is "truthy". None and false are falsey, everything else is truthy.
        """
        if obj is None:
            return False

        if isinstance(obj, bool):
            return bool(obj)

        return True

    def _evaluate(self, expr):
        return expr.accept(self)
