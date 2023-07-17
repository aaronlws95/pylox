class ReturnException(Exception):
    """
    Wrapper for return exception to unwind stack and return early if necessasry
    """

    def __init__(self, value: object):
        super().__init__()
        self.value = value
