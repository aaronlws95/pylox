from typing import List

from utils.expr import Expr


class AstPrinter(Expr.Visitor):
    """
    Prints the abstract syntax tree
    """

    def print(self, expr: Expr) -> str:
        return expr.accept(self)

    def parenthesize(self, name: str, exprs: List[Expr]) -> str:
        out = f"({name}"
        for expr in exprs:
            out += f" {expr.accept(self)}"
        out += ")"
        return out

    def visit_binary_expr(self, expr) -> str:
        return self.parenthesize(expr.operator.lexeme, [expr.left, expr.right])

    def visit_grouping_expr(self, expr) -> str:
        return self.parenthesize("group", [expr.expression])

    def visit_literal_expr(self, expr) -> str:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr) -> str:
        return self.parenthesize(expr.operator.lexeme, [expr.right])
