import io
import unittest
import unittest.mock

from pylox import PyLox
from utils.scanner import Scanner
from utils.token import Token
from utils.token_type import TokenType


class TestScanner(unittest.TestCase):
    def test_is_at_end(self):
        scanner = Scanner(None, "abc")
        scanner._current = 2
        self.assertFalse(scanner._is_at_end())

        scanner._current = 3
        self.assertTrue(scanner._is_at_end())

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_add_string(self, mock_stdout):
        # unterminated string
        scanner = Scanner(PyLox, '"unterminated')
        scanner._advance()
        scanner._add_string()
        self.assertEqual(mock_stdout.getvalue(), "[line 1] Error  : Unterminated string\n")

        # regular string
        scanner = Scanner(PyLox, '"hello"')
        scanner._advance()
        scanner._add_string()
        self.assertEqual(len(scanner._tokens), 1)
        self.assertEqual(scanner._tokens[0], Token(TokenType.STRING, '"hello"', "hello", 1))

        # multi-line string
        scanner = Scanner(PyLox, '"hello\nthere"')
        scanner._advance()
        scanner._add_string()
        self.assertEqual(len(scanner._tokens), 1)
        self.assertEqual(scanner._tokens[0], Token(TokenType.STRING, '"hello\nthere"', "hello\nthere", 2))

    def test_add_digit(self):
        # integer
        scanner = Scanner(None, "1015")
        scanner._add_number()
        self.assertEqual(len(scanner._tokens), 1)
        self.assertEqual(scanner._tokens[0], Token(TokenType.NUMBER, "1015", 1015, 1))

        # decimal
        scanner = Scanner(None, "1015.2556")
        scanner._add_number()
        self.assertEqual(len(scanner._tokens), 1)
        self.assertEqual(scanner._tokens[0], Token(TokenType.NUMBER, "1015.2556", 1015.2556, 1))

    def test_add_identifier(self):
        # keyword
        scanner = Scanner(None, "and")
        scanner._current = 3
        scanner._add_identifier()
        self.assertEqual(len(scanner._tokens), 1)
        self.assertEqual(scanner._tokens[0], Token(TokenType.AND, "and", None, 1))

        # identifier
        scanner = Scanner(None, "x1y2z")
        scanner._advance()
        scanner._add_identifier()
        self.assertEqual(len(scanner._tokens), 1)
        self.assertEqual(scanner._tokens[0], Token(TokenType.IDENTIFIER, "x1y2z", None, 1))

    def test_peek(self):
        scanner = Scanner(None, "blabla")
        self.assertEqual(scanner._peek(), "b")
        scanner._current = 6
        self.assertEqual(scanner._peek(), "\0")

    def test_peek_next(self):
        scanner = Scanner(None, "blabla")
        self.assertEqual(scanner._peek_next(), "l")
        scanner._current = 5
        self.assertEqual(scanner._peek_next(), "\0")

    def test_match(self):
        scanner = Scanner(None, "blabla")
        self.assertTrue(scanner._match("b"))
        self.assertEqual(scanner._current, 1)
        self.assertFalse(scanner._match("b"))
        self.assertEqual(scanner._current, 1)
        scanner._current = 6
        self.assertFalse(scanner._match("b"))

    def test_advance(self):
        scanner = Scanner(None, "blabla")
        self.assertEqual(scanner._advance(), "b")
        self.assertEqual(scanner._current, 1)
        scanner._current = 6
        with self.assertRaises(IndexError):
            scanner._advance()

    def test_add_token(self):
        scanner = Scanner(None, "blabla")
        scanner._current = 6
        scanner._add_token(TokenType.IDENTIFIER, None)

        self.assertEqual(len(scanner._tokens), 1)
        self.assertEqual(scanner._tokens[0], Token(TokenType.IDENTIFIER, "blabla", None, 1))

    def test_is_digit(self):
        for i in range(10):
            self.assertTrue(Scanner._is_digit(str(i)))
        self.assertTrue(Scanner._is_digit(str(1234567)))
        self.assertTrue(Scanner._is_digit(str(1234567.56778)))
        self.assertFalse(Scanner._is_digit("a"))
        self.assertFalse(Scanner._is_digit(str(-1)))

    def test_is_alpha(self):
        self.assertTrue(Scanner._is_alpha("g"))
        self.assertTrue(Scanner._is_alpha("_"))
        self.assertTrue(Scanner._is_alpha("J"))
        self.assertTrue(Scanner._is_alpha("hello"))
        self.assertFalse(Scanner._is_alpha("-"))
        self.assertFalse(Scanner._is_alpha(""))
        self.assertFalse(Scanner._is_alpha("566"))
