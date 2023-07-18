from typing import List, Union

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
    Super,
    This,
    Unary,
    Variable,
)
from utils.stmt import (
    Block,
    Class,
    Expression,
    Function,
    If,
    Print,
    Return,
    Stmt,
    Var,
    While,
)
from utils.token import Token


class AstPrinter(Expr.Visitor, Stmt.Visitor):
    """
    Prints the abstract syntax tree
    """

    def print(self, target: Union[Expr, Stmt]) -> str:
        return target.accept(self)

    def parenthesize(self, name: str, targets: List[Union[Expr, Stmt, List, Token, str]]) -> str:
        out = f"({name}"
        out = self.transform(out, targets)
        out += ")"
        return out

    def transform(self, out: str, targets: List[Union[Expr, Stmt, List, Token, str]]) -> str:
        for target in targets:
            if isinstance(target, Expr) or isinstance(target, Stmt):
                out += f" {self.print(target)}"
            elif isinstance(target, Token):
                out += f" {target.lexeme}"
            elif isinstance(target, list):
                if target:
                    out += self.transform(out, target)
            else:
                out += target
        return out

    def visit_block_stmt(self, stmt: Block) -> str:
        return self.parenthesize("block", stmt.statements)

    def visit_expression_stmt(self, stmt: Expression) -> str:
        return self.parenthesize(";", [stmt.expression])

    def visit_class_stmt(self, stmt: Class) -> str:
        out = f"(class {stmt.name.lexeme}"
        if stmt.superclass is not None:
            out += f" < {self.print(stmt.superclass)}"

        for method in stmt.methods:
            out += f" {self.print(method)}"

        out += ")"
        return out

    def visit_function_stmt(self, stmt: Function) -> str:
        out = f"( fun {stmt.name.lexeme} ("

        for param in stmt.params:
            if param != stmt.params[0]:
                out += " "
            out += param.lexeme

        out += ")"

        for body in stmt.body:
            out += self.print(body)

        out += ")"

        return out

    def visit_if_stmt(self, stmt: If) -> str:
        if stmt.else_branch is None:
            return self.parenthesize("if", [stmt.condition, stmt.then_branch])

        return self.parenthesize("if-else", [stmt.condition, stmt.then_branch, stmt.else_branch])

    def visit_print_stmt(self, stmt: Print) -> str:
        return self.parenthesize("print", [stmt.expression])

    def visit_return_stmt(self, stmt: Return) -> str:
        if stmt.value is None:
            return "(return)"

        return self.parenthesize("return", [stmt.value])

    def visit_var_stmt(self, stmt: Var) -> str:
        if stmt.initializer is None:
            return self.parenthesize("var", [stmt.name])

    def visit_while_stmt(self, stmt: While) -> str:
        return self.parenthesize("while", [stmt.condition, stmt.body])

    def visit_assign_expr(self, expr: Assign) -> str:
        return self.parenthesize("=", [expr.name.lexeme, expr.value])

    def visit_call_expr(self, expr: Call) -> str:
        return self.parenthesize("call", [expr.callee, expr.arguments])

    def visit_get_expr(self, expr: Get) -> str:
        return self.parenthesize(".", [expr.obj, expr.name.lexeme])

    def visit_logical_expr(self, expr: Logical) -> str:
        return self.parenthesize(expr.operator.lexeme, [expr.left, expr.right])

    def visit_set_expr(self, expr: Set) -> str:
        return self.parenthesize("=", [expr.obj, expr.name.lexeme, expr.value])

    def visit_super_expr(self, expr: Super) -> str:
        return self.parenthesize("super", [expr.method])

    def visit_this_expr(self, expr: This) -> str:
        return "this"

    def visit_variable_expr(self, expr: Variable) -> str:
        return expr.name.lexeme

    def visit_binary_expr(self, expr: Binary) -> str:
        return self.parenthesize(expr.operator.lexeme, [expr.left, expr.right])

    def visit_grouping_expr(self, expr: Grouping) -> str:
        return self.parenthesize("group", [expr.expression])

    def visit_literal_expr(self, expr: Literal) -> str:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr: Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, [expr.right])
