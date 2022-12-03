"""
Script to generate expr.py. We use this to ease adding expr types to the Abstract Syntax Tree (AST).
"""

import argparse
from pathlib import Path
from typing import List


def parse_args() -> argparse.Namespace:
    """
    Parse arguments
    """
    parser = argparse.ArgumentParser(prog="generate_ast", description="Abstract Syntax Tree class generator")

    parser.add_argument("-o", "--out_dir", default="../src/utils/", type=str, help="Output directory")

    return parser.parse_args()


def define_ast(out_dir: str, base_name: str, types: List[str]):
    """
    Generate the AST class file (expr.py)
    """
    out_path = Path(out_dir) / (base_name.lower() + ".py")

    base_class_str = f"""
from abc import ABC, abstractmethod
from utils.token import Token


class Expr(ABC):
    {define_visitor(base_name, types)}
    @abstractmethod
    def accept(self, visitor: Visitor):
        pass

    """

    with open(out_path, "w") as f:
        f.write(base_class_str)
        for t in types:
            class_name = t.split("=")[0].strip()
            fields = t.split("=")[1].strip()
            f.write(define_type(base_name, class_name, fields))
            f.write("\n")


def define_visitor(base_name, types):
    """
    Generate Visitor class to ease adding functions that work for each expr type (see ast_printer.py)
    """
    lines = []
    lines.append("    class Visitor(ABC):")

    for t in types:
        class_name = t.split("=")[0].strip()
        lines.append("")
        lines.append("        @abstractmethod")
        lines.append(f"        def visit_{class_name.lower()}_{base_name.lower()}(self, expr):")
        lines.append("            pass")

    out_str = "\n".join(lines)
    return f"""
{out_str}
        """


def define_type(base_name: str, class_name: str, field_list: str):
    """
    Generate expr type classes
    """
    lines = []
    lines.append(f"class {class_name}({base_name}):")
    lines.append(f"    def __init__(self, {field_list}):")
    for field in field_list.split(", "):
        name = field.split(": ")[0].lower()
        lines.append(f"        self.{name} = {name}")
    lines.append("")
    lines.append("    def accept(self, visitor: Expr.Visitor):")
    lines.append(f"        return visitor.visit_{class_name.lower()}_{base_name.lower()}(self)")

    out_str = "\n".join(lines)
    return f"""
{out_str}
        """


if __name__ == "__main__":
    args = parse_args()

    types = [
        "Binary   = left: Expr, operator: Token, right: Expr",
        "Grouping = expression: Expr",
        "Literal  = value: object",
        "Unary    = operator: Token, right: Expr",
    ]

    define_ast(args.out_dir, "Expr", types)
