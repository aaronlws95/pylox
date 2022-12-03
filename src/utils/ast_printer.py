from typing import List

from utils.expr import Expr


class AstPrinter(Expr.Visitor):
    def print(self, expr: Expr):
        return expr.accept(self)

    def parenthesize(self, name: str, exprs: List[Expr]):
        out = f"({name}"
        for expr in exprs:
            out += f" {expr.accept(self)}"
        out += ")"
        return out

    def visit_binary_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, [expr.left, expr.right])

    def visit_grouping_expr(self, expr):
        return self.parenthesize("group", [expr.expression])

    def visit_literal_expr(self, expr):
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, [expr.right])
