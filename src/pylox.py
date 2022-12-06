import argparse
import sys
from pathlib import Path

from utils.scanner import Scanner
from utils.token_type import TokenType
from utils.parser import Parser
from utils.ast_printer import AstPrinter
from utils.runtime_error import PyLoxRuntimeError
from utils.interpreter import Interpreter


def parse_args() -> argparse.Namespace:
    """
    Parse arguments
    """
    parser = argparse.ArgumentParser(
        prog="pylox",
        description="PyLox Interpreter",
        epilog="PyLox is based on the Lox language from 'Crafting Intrepreters' written by Bob Nystrom",
    )

    parser.add_argument("-s", "--script", default=None, type=str, help="'.lox' script to interpret")

    return parser.parse_args()


class PyLox:
    _had_error = False
    _had_runtime_error = False
    _interpreter = Interpreter()

    @staticmethod
    def run_prompt() -> None:
        """
        Run in REPL mode
        """
        while True:
            try:
                line = input("> ")
                if line == "quit":
                    break
                PyLox.run(line)
                PyLox._had_error = False
            except EOFError:
                break

    @staticmethod
    def run_file(path: Path):
        """
        Run code from file
        """
        with open(path, "r") as f:
            PyLox.run(f.read())
            if PyLox._had_error:
                sys.exit(65)
            if PyLox._had_runtime_error:
                sys.exit(70)

    @staticmethod
    def run(source: str) -> None:
        """
        Run interpreter on a source line
        """
        scanner = Scanner(PyLox, source)
        tokens = scanner.scan_tokens()
        parser = Parser(PyLox, tokens)
        statements = parser.parse()

        if PyLox._had_error:
            return

        PyLox._interpreter.interpret(PyLox, statements)

    @staticmethod
    def error_line(line: int, message: str) -> None:
        """
        Report error at a given line
        """
        PyLox.report(line, "", message)

    @staticmethod
    def error_token(token, message):
        """
        Report error when parsing a token
        """
        if token.token_type == TokenType.EOF:
            PyLox.report(token.line, " at end", message)
        else:
            PyLox.report(token.line, " at '" + token.lexeme + "'", message)

    @staticmethod
    def runtime_error(error: PyLoxRuntimeError):
        print(f"{error.message}\n[line {error.token.line}]")
        PyLox._had_runtime_error = True

    @staticmethod
    def report(line: int, where: str, message: str) -> None:
        """
        Print an error message
        """

        print(f"[line {line}] Error {where} : {message}")

        PyLox._had_error = True


if __name__ == "__main__":
    args = parse_args()

    if args.script is not None:
        PyLox.run_file(Path(args.script))
    else:
        PyLox.run_prompt()
