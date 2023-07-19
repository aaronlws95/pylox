# PyLox
A tree-walk interpreter for the Lox language as defined in [Crafting Interpreters](https://craftinginterpreters.com/) written by [Bob Nystrom](https://github.com/munificent). 

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

