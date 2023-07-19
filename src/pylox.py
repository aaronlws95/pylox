import argparse
import sys
from pathlib import Path

from utils.ast_printer import AstPrinter
from utils.interpreter import Interpreter
from utils.parser import Parser
from utils.resolver import Resolver
from utils.runtime_error import PyLoxRuntimeError
from utils.scanner import Scanner
from utils.token_type import TokenType


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
    parser.add_argument("--ast", action="store_true", help="Run with abstract syntax tree printer")

    return parser.parse_args()


class PyLox:
    _had_error = False
    _had_runtime_error = False
    _interpreter = Interpreter()
    _ast_printer = AstPrinter()

    @staticmethod
    def run_prompt(use_ast_printer: bool) -> None:
        """
        Run in REPL mode
        """
        while True:
            try:
                line = input("> ")
                if line == "quit":
                    break
                PyLox.run(line, use_ast_printer)
                PyLox._had_error = False
            except EOFError:
                break

    @staticmethod
    def run_file(path: Path, use_ast_printer: bool) -> None:
        """
        Run code from file
        """
        with open(path, "r") as f:
            PyLox.run(f.read(), use_ast_printer)
            if PyLox._had_error:
                sys.exit(65)
            if PyLox._had_runtime_error:
                sys.exit(70)

    @staticmethod
    def run(source: str, use_ast_printer: bool) -> None:
        """
        Run interpreter on a source line
        """
        scanner = Scanner(PyLox, source)
        tokens = scanner.scan_tokens()
        parser = Parser(PyLox, tokens)
        statements = parser.parse()
        if PyLox._had_error:
            return

        interpreter = PyLox._interpreter

        resolver = Resolver(PyLox, interpreter)
        resolver.resolve(statements)
        if PyLox._had_error:
            return

        if use_ast_printer:
            for statement in statements:
                print(PyLox._ast_printer.print(statement))
        else:
            interpreter.interpret(PyLox, statements)

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
        print(f"[line {error.token.line}]: {error.message} ")
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
        PyLox.run_file(Path(args.script), args.ast)
    else:
        PyLox.run_prompt(args.ast)
