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

