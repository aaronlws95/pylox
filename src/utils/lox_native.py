import time
from typing import List

from utils.lox_callable import LoxCallable


class Clock(LoxCallable):
    """
    Native function that returns current time in seconds
    """

    def call(interpreter, arguments: List[object]) -> object:
        return time.time()

    def arity(self):
        return 0

    def to_string():
        return "<native fn>"
