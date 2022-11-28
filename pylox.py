import sys
import argparse

from pathlib import Path
from token_type import TokenType


def parse_args() -> argparse.Namespace:
    """
    Parse arguments
    """
    parser = argparse.ArgumentParser(
        prog="pylox",
        description="PyLox Interpreter",
        epilog="PyLox is based on the Lox language from 'Crafting Intrepreters' written by Bob Nystrom",
    )

    parser.add_argument("-s", "--script", action="store_true", help="'.lox' script to interpret")

    return parser.parse_args()


class PyLox:
    def __init__(self):
        self.hadError = False

    def run_prompt(self) -> None:
        while True:
            try:
                line = input("> ")
                if line == "quit":
                    break
                self.run(line)
                self.hadError = False
            except EOFError:
                break

    def run_file(self, path: Path):
        with open(path, "rb") as f:
            while byte := f.read(1):
                self.run(byte.decode("utf-8"))
                if self.hadError:
                    sys.exit(65)

    def run(self, source: str) -> None:
        """
        Run interpreter on a source line
        """
        scanner = Scanner()
        tokens = scanner.scan_tokens()

        for token in tokens:
            print(token)

    def error(self, line: int, message: str) -> None:
        """
        Report error
        """
        self.report(line, "", message)

    def report(self, line: int, where: str, message, str) -> None:
        """
        Print an error message
        """

        print(f"[line {line}] Error {where} : {message}")
        self.hadError = True


if __name__ == "__main__":
    args = parse_args()

    x = TokenType.LEFT_PAREN

    # if args.script:
