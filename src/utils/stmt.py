
from abc import ABC, abstractmethod
from typing import List
from utils.expr import Expr
from utils.token import Token


class Stmt(ABC):
    class Visitor(ABC):

        @abstractmethod
        def visit_block_stmt(self, stmt):
            pass

        @abstractmethod
        def visit_expression_stmt(self, stmt):
            pass

        @abstractmethod
        def visit_print_stmt(self, stmt):
            pass

        @abstractmethod
        def visit_var_stmt(self, stmt):
            pass
    @abstractmethod
    def accept(self, visitor: Visitor):
        pass

    
class Block(Stmt):
    def __init__(self, statements: List[Stmt]):
        self.statements = statements

    def accept(self, visitor: Expr.Visitor):
        return visitor.visit_block_stmt(self)
        

class Expression(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: Expr.Visitor):
        return visitor.visit_expression_stmt(self)
        

class Print(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: Expr.Visitor):
        return visitor.visit_print_stmt(self)
        

class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: Expr.Visitor):
        return visitor.visit_var_stmt(self)
        
