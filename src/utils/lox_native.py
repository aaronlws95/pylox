import time
from typing import List

from utils.lox_callable import LoxCallable


class Clock(LoxCallable):
    """
    Native function that returns current time in seconds
    """

    def call(self, interpreter, arguments: List[object]) -> object:
        return time.time()

    def arity(self):
        return 0

    def __str__(self):
        return "<native fn clock>"
