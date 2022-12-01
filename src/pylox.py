import argparse
import sys
from pathlib import Path

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

    return parser.parse_args()


class PyLox:
    hadError = False

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
                hadError = False
            except EOFError:
                break

    @staticmethod
    def run_file(path: Path):
        """
        Run code from file
        """
        with open(path, "rb") as f:
            while byte := f.read(1):
                PyLox.run(byte.decode("utf-8"))
                if hadError:
                    sys.exit(65)

    @staticmethod
    def run(source: str) -> None:
        """
        Run interpreter on a source line
        """
        scanner = Scanner(PyLox, source)
        tokens = scanner.scan_tokens()

        for token in tokens:
            print(token)

    @staticmethod
    def error(line: int, message: str) -> None:
        """
        Report error
        """
        PyLox.report(line, "", message)

    @staticmethod
    def report(line: int, where: str, message: str) -> None:
        """
        Print an error message
        """

        print(f"[line {line}] Error {where} : {message}")

        hadError = True


if __name__ == "__main__":
    args = parse_args()

    if args.script is not None:
        PyLox.run_file(Path(args.script))
    else:
        PyLox.run_prompt()
