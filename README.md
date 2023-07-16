# PyLox
Interpreter based on the Lox language from [Crafting Interpreters](https://craftinginterpreters.com/) written by [Bob Nystrom](https://github.com/munificent). 

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