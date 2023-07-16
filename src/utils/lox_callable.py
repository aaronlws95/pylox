from abc import ABC, abstractmethod
from typing import List


class LoxCallable(ABC):
    """
    Interface for objects that can be called like a function
    """

    @abstractmethod
    def call(self, interpreter, arguments: List[object]) -> object:
        pass

    @abstractmethod
    def arity(self) -> int:
        """
        Number of arguments the function expects
        """
        pass

    @abstractmethod
    def to_string(self) -> str:
        pass
