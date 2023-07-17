from utils.lox_callable import LoxCallable
from utils.lox_instance import LoxInstance
from utils.lox_function import LoxFunction
from typing import List, Dict


class LoxClass(LoxCallable):
    def __init__(self, name: str, methods: Dict[str, LoxFunction]):
        self.name = name
        self.methods = methods

    def call(self, interpreter, arguments: List[object]) -> object:
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)

        return instance

    def find_method(self, name: str) -> LoxFunction:
        if name in self.methods:
            return self.methods[name]

    def arity(self):
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()

    def __str__(self):
        return self.name
