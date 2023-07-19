# PyLox
A tree-walk interpreter for the Lox language as defined in Part II of [Crafting Interpreters](https://craftinginterpreters.com/) written by [Bob Nystrom](https://github.com/munificent). 

Lox is an object-oriented, dynamically-typed programming language following C-style syntax.

## Instructions

### Requirements
- Python 3.10

```bash
make conda
conda activate pylox
```

### Run
Use the `--ast` flag to run with the abstract syntax tree print output
```bash
./pylox # Run REPL, currently does not support multi-line blocks
./pylox -s <optional_script_path> # Run Lox script 
```

### Test
```bash
make coverage
```

### Formatting
```bash
make format
```

## Grammar
```bash
program        -> declaration* EOF ;
declaration    -> classDecl
                | funDecl
                | varDecl
                | statement ;
classDecl      -> "class" IDENTIFIER ( "<" IDENTIFIER )?
                "{" function* "}" ;
funDecl        -> "fun" function ;
function       -> IDENTIFIER "(" parameters? ")" block ;
parameters     -> IDENTIFIER ( "," IDENTIFIER )* ;
varDecl        -> "var" IDENTIFIER ( "=" expression )? ";" ;
statement      -> exprStmt
                | forStmt
                | ifStmt
                | printStmt
                | returnStmt
                | whileStmt
                | block ;
returnStmt      -> "return" expression? ";" ;
forStmt         -> "for" "(" ( varDecl | exprStmt | ";" )
                expression? ";"
                expression? ")" statement ;
whileStmt      -> "while" "(" expression ")" statement ;
block          -> "{" declaration* "}" ;
exprStmt       -> expression ";"
ifStmt         -> "if" "(" expression ")" statement
                ( "else" statement )? ;
printStmt      -> "print" expression ";" ;
expression     -> assignment ;
assignment     -> ( call "." )? IDENTIFIER "=" assignment
                | logic_or ;
logic_or       -> logic_and ( "or" logic_and )* ;
logic_and      -> equality ( "and" equality )* ;
equality       -> comparison ( ( "!=" | "==" ) comparison )* ;
comparison     -> term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
term           -> factor ( ( "-" | "+" ) factor )* ;
factor         -> unary ( ( "/" | "*" ) unary )* ;
unary          -> ( "!" | "-" ) unary
                | primary ;
call           -> primary ( "(" arguments? ")" | "." IDENTIFIER )* ;
arguments      -> expression ( "," expression )* ;
primary        -> "true" | "false" | "nil" | "this"
                | NUMBER | STRING | IDENTIFIER | "(" expression ")"
                | "super" "." IDENTIFIER
```

## Test Coverage
```bash
Name                            Stmts   Miss  Cover
---------------------------------------------------
src/pylox.py                       76     42    45%
src/tests/__init__.py               0      0   100%
src/tests/test_ast_printer.py       0      0   100%
src/tests/test_parser.py           57      0   100%
src/tests/test_scanner.py         159      0   100%
src/tests/test_token.py            11      0   100%
src/utils/__init__.py               0      0   100%
src/utils/ast_printer.py           87     58    33%
src/utils/environment.py           32     18    44%
src/utils/expr.py                 116     43    63%
src/utils/interpreter.py          213    162    24%
src/utils/lox_callable.py          12      3    75%
src/utils/lox_class.py             27     17    37%
src/utils/lox_function.py          31     19    39%
src/utils/lox_instance.py          16     10    38%
src/utils/lox_native.py            10      3    70%
src/utils/parser.py               275    146    47%
src/utils/resolver.py             154    108    30%
src/utils/return_exception.py       4      2    50%
src/utils/runtime_error.py          6      3    50%
src/utils/scanner.py              117      0   100%
src/utils/stmt.py                  90     36    60%
src/utils/token.py                 13      1    92%
src/utils/token_type.py            41      0   100%
---------------------------------------------------
TOTAL                            1547    671    57%
```

## TODO
- [ ] More tests
- [ ] Challenges
- [ ] Make REPL more nice to use