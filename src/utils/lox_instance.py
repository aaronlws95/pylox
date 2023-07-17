class LoxInstance:
    def __init__(self, klass):
        self.klass = klass

    def __str__(self):
        return f"{self.klass.name} instance"
