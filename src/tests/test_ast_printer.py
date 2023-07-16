# import unittest

# from utils.ast_printer import AstPrinter
# from utils.expr import Binary, Grouping, Literal, Unary
# from utils.token import Token
# from utils.token_type import TokenType


# class TestAstPrinter(unittest.TestCase):
#     def test_print(self):
#         expression = Binary(
#             Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123)),
#             Token(TokenType.STAR, "*", None, 1),
#             Grouping(Literal(45.67)),
#         )

#         ast_printer = AstPrinter()
#         self.assertEqual(ast_printer.print(expression), "(* (- 123) (group 45.67))")
