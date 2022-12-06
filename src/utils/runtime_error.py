class PyLoxRuntimeError(Exception):
    def __init__(self, token, message):
        super().__init__(message)
        self.message = message
        self.token = token
