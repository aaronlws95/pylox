from typing import List

from utils.environment import Environment
from utils.lox_callable import LoxCallable
from utils.return_exception import ReturnException
from utils.stmt import Function


class LoxFunction(LoxCallable):
    """
    Implements LoxCallable so that we can call it
    """

    def __init__(self, declaration: Function, closure: Environment):
        self._declaration = declaration
        self._closure = closure

    def call(self, interpreter, arguments: List[object]) -> None:
        environment = Environment(self._closure)
        for i in range(len(self._declaration.params)):
            environment.define(self._declaration.params[i].lexeme, arguments[i])

        try:
            interpreter._execute_block(self._declaration.body, environment)
        except ReturnException as e:
            return e.value

    def arity(self) -> int:
        return len(self._declaration.params)

    def __str__(self) -> str:
        return f"<fn {self._declaration.name.lexeme}"
