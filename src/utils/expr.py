from abc import ABC, abstractmethod

from utils.token import Token


class Expr(ABC):
    class Visitor(ABC):
        @abstractmethod
        def visit_binary_expr(self, expr):
            pass

        @abstractmethod
        def visit_grouping_expr(self, expr):
            pass

        @abstractmethod
        def visit_literal_expr(self, expr):
            pass

        @abstractmethod
        def visit_unary_expr(self, expr):
            pass

    @abstractmethod
    def accept(self, visitor: Visitor):
        pass


class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: Expr.Visitor):
        return visitor.visit_binary_expr(self)


class Grouping(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: Expr.Visitor):
        return visitor.visit_grouping_expr(self)


class Literal(Expr):
    def __init__(self, value: object):
        self.value = value

    def accept(self, visitor: Expr.Visitor):
        return visitor.visit_literal_expr(self)


class Unary(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def accept(self, visitor: Expr.Visitor):
        return visitor.visit_unary_expr(self)
