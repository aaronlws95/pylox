import unittest

from pylox import PyLox
from utils.parser import Parser, ParseError
from utils.token import Token
from utils.token_type import TokenType


class TestParser(unittest.TestCase):
    def test_parse_equality(self):
        tokens = [
            Token(TokenType.NUMBER, "5", 5, 1),
            Token(TokenType.EQUAL_EQUAL, "==", None, 1),
            Token(TokenType.NUMBER, "10", 10, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(PyLox, tokens)

        statements = parser.parse()
        self.assertEqual(len(statements), 1)
        expression = statements[0].expression
        self.assertEqual(expression.left.value, 5)
        self.assertEqual(expression.operator, Token(TokenType.EQUAL_EQUAL, "==", None, 1))
        self.assertEqual(expression.right.value, 10)

    def test_parse_comparison(self):
        tokens = [
            Token(TokenType.NUMBER, "5", 5, 1),
            Token(TokenType.GREATER_EQUAL, ">=", None, 1),
            Token(TokenType.NUMBER, "10", 10, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(PyLox, tokens)

        statements = parser.parse()
        self.assertEqual(len(statements), 1)
        expression = statements[0].expression
        self.assertEqual(expression.left.value, 5)
        self.assertEqual(expression.operator, Token(TokenType.GREATER_EQUAL, ">=", None, 1))
        self.assertEqual(expression.right.value, 10)

    def test_parse_term(self):
        tokens = [
            Token(TokenType.NUMBER, "5", 5, 1),
            Token(TokenType.PLUS, "+", None, 1),
            Token(TokenType.NUMBER, "10", 10, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(PyLox, tokens)

        statements = parser.parse()
        self.assertEqual(len(statements), 1)
        expression = statements[0].expression
        self.assertEqual(expression.left.value, 5)
        self.assertEqual(expression.operator, Token(TokenType.PLUS, "+", None, 1))
        self.assertEqual(expression.right.value, 10)

    def test_parse_factor(self):
        tokens = [
            Token(TokenType.NUMBER, "5", 5, 1),
            Token(TokenType.STAR, "*", None, 1),
            Token(TokenType.NUMBER, "10", 10, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(PyLox, tokens)

        statements = parser.parse()
        self.assertEqual(len(statements), 1)
        expression = statements[0].expression
        self.assertEqual(expression.left.value, 5)
        self.assertEqual(expression.operator, Token(TokenType.STAR, "*", None, 1))
        self.assertEqual(expression.right.value, 10)

    def test_parse_unary(self):
        tokens = [
            Token(TokenType.BANG, "!", None, 1),
            Token(TokenType.NUMBER, "10", 10, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(PyLox, tokens)

        statements = parser.parse()
        self.assertEqual(len(statements), 1)
        expression = statements[0].expression
        self.assertEqual(expression.operator, Token(TokenType.BANG, "!", None, 1))
        self.assertEqual(expression.right.value, 10)

    def test_parse_primary(self):
        tokens = [
            Token(TokenType.NUMBER, "10", 10, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1),
        ]
        parser = Parser(PyLox, tokens)

        statements = parser.parse()
        self.assertEqual(len(statements), 1)
        expression = statements[0].expression
        self.assertEqual(expression.value, 10)
