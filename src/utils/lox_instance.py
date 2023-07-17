from utils.token import Token


class LoxInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}

    def get(self, name: Token) -> object:
        if name in self.fields:
            return self.fields[name]

        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise RuntimeError(name, f"Undefined property {name.lexeme}.")

    def sett(self, name: Token, value: object) -> None:
        self.fields[name] = value

    def __str__(self):
        return f"{self.klass.name} instance"
