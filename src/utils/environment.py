from typing import Dict
from utils.token import Token
from utils.runtime_error import PyLoxRuntimeError


class Environment:
    def __init__(self, environment=None):
        self._values: Dict[str, object] = {}
        self._enclosing: Environment = environment

    def define(self, name: str, value: object):
        self._values[name] = value

    def get(self, name: Token):
        if name.lexeme in self._values:
            return self._values[name.lexeme]

        if self._enclosing is not None:
            return self._enclosing.get(name)

        raise PyLoxRuntimeError(name, f"Undefined variable {name.lexeme}")

    def assign(self, name: Token, value: object):
        if name.lexeme in self._values:
            self._values[name.lexeme] = value
            return

        if self._enclosing is not None:
            return self._enclosing.assign(name, value)

        raise PyLoxRuntimeError(name, f"Undefined variable {name.lexeme}")
