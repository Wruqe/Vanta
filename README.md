# Vanta

Vanta is a small language implementation developed one compiler stage at a time.

- Lab 1: lexical scanning (`src/scanner.py`)
- Lab 2: expression ASTs and parenthesized printing (`src/expr.py` and
  `src/ast_printer.py`)

Run the current test suites from the repository root:

```bash
python3 -m unittest discover -s test/lab1 -p 'test_*.py' -v
python3 -m unittest discover -s test/lab2 -p 'test_*.py' -v
```
