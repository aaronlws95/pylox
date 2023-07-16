from utils.token import Token


class PyLoxRuntimeError(Exception):
    """
    Runtime error exception for PyLox
    """

    def __init__(self, token: Token, message: str):
        """
        :param token: Token related to the error
        :param message: Error message
        """
        super().__init__(message)
        self.message = message
        self.token = token
