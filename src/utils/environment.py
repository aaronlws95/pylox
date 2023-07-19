from typing import Dict

from utils.runtime_error import PyLoxRuntimeError
from utils.token import Token


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
        """
        Get variable value at a given scope depth
        """
        if name in self._ancestor(distance)._values:
            return self._ancestor(distance)._values[name]

    def assign_at(self, distance: int, name: Token, value: object) -> None:
        """
        Assign value to variable at a given scope depth
        """
        self._ancestor(distance)._values[name.lexeme] = value

    def _ancestor(self, distance: int):
        """
        Get corresponding environment at a given depth
        """
        environment = self
        for _ in range(distance):
            environment = environment._enclosing
        return environment

    def assign(self, name: Token, value: object) -> None:
        """
        Assign variable to value and save in _values
        """
        if name.lexeme in self._values:
            self._values[name.lexeme] = value
            return

        if self._enclosing is not None:
            return self._enclosing.assign(name, value)

        raise PyLoxRuntimeError(name, f"Undefined variable {name.lexeme}")
