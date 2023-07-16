import time
from utils.lox_callable import LoxCallable
from typing import List


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
