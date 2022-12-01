import unittest

from utils.token import Token
from utils.token_type import TokenType


class TestToken(unittest.TestCase):
    def test_token(self):
        a = Token(TokenType.AND, TokenType.AND.value, None, 1)
        self.assertEqual(a.token_type, TokenType.AND)
        self.assertEqual(a.lexeme, TokenType.AND.value)
        self.assertIsNone(a.literal)
        self.assertEqual(a.line, 1)
        self.assertEqual(a.__str__(), "TokenType.AND and None")
