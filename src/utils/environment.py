from typing import Dict
from utils.token import Token
from utils.runtime_error import PyLoxRuntimeError


class Environment:
    """
    Storage for bindings of associated variables to _values
    """

    def __init__(self, environment=None):
        self._values: Dict[str, object] = {}
        self._enclosing: Environment = environment  # enclosing scope

    def define(self, name: str, value: object) -> None:
        self._values[name] = value

    def get(self, name: Token) -> object:
        if name.lexeme in self._values:
            return self._values[name.lexeme]

        if self._enclosing is not None:
            return self._enclosing.get(name)

        raise PyLoxRuntimeError(name, f"Undefined variable {name.lexeme}")

    def get_at(self, distance: int, name: str) -> object:
        return self._ancestor(distance)._values.get(name)

    def assign_at(self, distance: int, name: Token, value: object) -> None:
        self._ancestor(distance)._values[name.lexeme] = value

    def _ancestor(self, distance: int):
        environment = self
        for _ in range(distance):
            environment = environment._enclosing
        return environment

    def assign(self, name: Token, value: object) -> None:
        if name.lexeme in self._values:
            self._values[name.lexeme] = value
            return

        if self._enclosing is not None:
            return self._enclosing.assign(name, value)

        raise PyLoxRuntimeError(name, f"Undefined variable {name.lexeme}")
