# PyLox
A tree-walk interpreter for the Lox language as defined in [Crafting Interpreters](https://craftinginterpreters.com/) written by [Bob Nystrom](https://github.com/munificent). 

Lox is an object-oriented, dynamically-typed programming language following C-style syntax.

## Instructions
### Run
```bash
./pylox <optional_script_path>
```

### Test
```bash
tox -e unittest
coverage report -m # check coverage
```

### Formatting
```bash
tox -e format
tox -e lint
```

## Requirements
- Python 3.10

```bash
pip install -r requirements.txt
```
