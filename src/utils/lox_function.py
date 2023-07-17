from typing import List

from utils.environment import Environment
from utils.lox_callable import LoxCallable
from utils.lox_instance import LoxInstance
from utils.return_exception import ReturnException
from utils.stmt import Function


class LoxFunction(LoxCallable):
    """
    Implements LoxCallable so that we can call it
    """

    def __init__(self, declaration: Function, closure: Environment, is_initializer: bool):
        self._declaration = declaration
        self._closure = closure
        self._is_initializer = is_initializer

    def call(self, interpreter, arguments: List[object]) -> None:
        environment = Environment(self._closure)
        for i in range(len(self._declaration.params)):
            environment.define(self._declaration.params[i].lexeme, arguments[i])

        try:
            interpreter._execute_block(self._declaration.body, environment)
        except ReturnException as e:
            if self._is_initializer:
                return self._closure.get_at(0, "this")

            return e.value

        if self._is_initializer:
            return self._closure.get_at(0, "this")

    def arity(self) -> int:
        return len(self._declaration.params)

    @classmethod
    def bind(self, instance: LoxInstance):
        environment = Environment(self._closure)
        environment.define("this", instance)
        return LoxFunction(self._declaration, environment, self._is_initializer)

    def __str__(self) -> str:
        return f"<fn {self._declaration.name.lexeme}"
