from utils.lox_callable import LoxCallable
from utils.lox_instance import LoxInstance
from typing import List


class LoxClass(LoxCallable):
    def __init__(self, name: str):
        self.name = name

    def call(self, interpreter, arguments: List[object]) -> object:
        instance = LoxInstance(self)
        return instance

    def arity(self):
        return 0

    def __str__(self):
        return self.name
