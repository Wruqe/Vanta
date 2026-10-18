# Vanta Lab 3: Parser

## Overview

Lab 3 connects Vanta's scanner, expression AST classes, recursive-descent parser,
and AST printer. The program accepts one expression from a file or one expression
per interactive line, then prints the resulting tree. It does not evaluate or
execute the expression.

The Lab 2 `Expr`, `Binary`, `Unary`, `Grouping`, `Literal`, and `AstPrinter` classes
are reused without replacement. The parser creates those existing node types.

## Expression grammar

The grammar is unchanged from Lab 2. Rules appear from lowest to highest
precedence.

```text
expression  -> logic_or ;
logic_or    -> logic_and ( "or" logic_and )* ;
logic_and   -> equality ( "and" equality )* ;
equality    -> comparison ( ( "!=" | "==" ) comparison )* ;
comparison  -> term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
term        -> factor ( ( "-" | "+" ) factor )* ;
factor      -> unary ( ( "/" | "*" ) unary )* ;
unary       -> ( "!" | "-" ) unary | primary ;
primary     -> NUMBER | STRING | "true" | "false" | "null"
             | "(" expression ")" ;
```

### Precedence and associativity

From lowest to highest, precedence is `or`, `and`, equality, comparison, addition
and subtraction, multiplication and division, unary operators, then primary
expressions. Binary operators at the same level associate left because each parser
method builds a new left-hand tree inside a loop. Unary operators associate right
because `unary` recursively parses another `unary` as its operand. Parentheses
restart parsing from the full `expression` rule and preserve a `Grouping` node.

### Design relative to Lox

Vanta follows Lox's recursive-descent organization and precedence levels. Its null
literal is spelled `null` instead of `nil`, and scanned whole numbers remain Python
integers. Vanta retains `and` and `or` because they were already part of the Lab 2
grammar, even though Lab 3 does not require logical operators. They use the existing
`Binary` AST node because their stored structure is still left operand, operator,
and right operand.

No grammar changes were made since Lab 2. Identifiers, assignment, calls, and
statements remain outside this expression-only lab.

## Parser and error design

`Parser` keeps the token list and current position. One method implements each
precedence rule. A valid parse must reach EOF; otherwise the parser reports an
unexpected trailing token rather than ignoring it.

Syntax diagnostics contain the token's line and either its lexeme or `at end`.
The parser returns no AST after a syntax error. The main program also stops before
parsing when the scanner reports a lexical error, so invalid input never prints a
successful tree. File errors return status 65. Interactive input gets a fresh
scanner and parser on every prompt, allowing the next line to work normally.

Lab 1 token output is still available through `--tokens`; normal execution now
performs the Lab 3 scan-parse-print pipeline.

## Setup and execution

No third-party dependencies are required. Run commands from the repository root
with Python 3.

Parse a source file:

```bash
python3 src/main.py test/lab3/precedence.vanta
```

Start interactive mode:

```bash
python3 src/main.py
```

Run the Lab 3 tests:

```bash
python3 -m unittest discover -s test/lab3 -p 'test_*.py' -v
```

Run every lab suite:

```bash
python3 -m unittest discover -s test/lab1 -p 'test_*.py' -v
python3 -m unittest discover -s test/lab2 -p 'test_*.py' -v
python3 -m unittest discover -s test/lab3 -p 'test_*.py' -v
```

Manually reproduce the committed file cases:

```bash
python3 src/main.py test/lab3/grouping.vanta
python3 src/main.py test/lab3/missing_operand.vanta
python3 src/main.py test/lab3/missing_left_paren.vanta
python3 src/main.py test/lab3/missing_right_paren.vanta
python3 src/main.py test/lab3/unexpected_token.vanta
python3 src/main.py test/lab3/trailing_tokens.vanta
python3 src/main.py test/lab3/lexical_error.vanta
```

## Test cases and results

The results below were reproduced on October 17, 2026. Every `Actual` entry comes
from the automated assertion or a direct run of its committed fixture.

| Test and purpose | Source input | Expected | Actual | Match |
|---|---|---|---|---|
| Every literal type | `10`, `3.14`, `"hello"`, `true`, `false`, `null` | Each literal prints with its Vanta spelling | `10`; `3.14`; `"hello"`; `true`; `false`; `null` | Yes |
| Every binary operator | `8 op 2` for `+ - * / == != > >= < <=`; `true op false` for `and or` | A two-child AST for each operator | `(+ 8 2)` through `(<= 8 2)`, plus `(and true false)` and `(or true false)` | Yes |
| Precedence | `false or true and 1 + 2 * 3 == 7` | `(or false (and true (== (+ 1 (* 2 3)) 7)))` | Same | Yes |
| Left associativity | `10 - 3 - 2` | `(- (- 10 3) 2)` | Same | Yes |
| Unary and nested grouping | `!!false or -(3 + (4 * 2)) < 0` | `(or (! (! false)) (< (- (group (+ 3 (group (* 4 2))))) 0))` | Same | Yes |
| Missing operand | `1 +` | Line 1, at end: `Expected expression.` | Same diagnostic in direct parser test | Yes |
| Missing left operand | `+ 1` | Line 1 at `+`: `Expected expression.` | Same diagnostic | Yes |
| Missing right parenthesis | `(1 + 2` | At end: `Expected ')' after expression.` | Fixture: `[line 2] Error at end: Expected ')' after expression.` | Yes |
| Unmatched right parenthesis | `1 + 2)` | At `)`: `Unexpected token after expression.` | `[line 1] Error at ')': Unexpected token after expression.` | Yes |
| Unexpected keyword | `let` | At `let`: `Expected expression.` | `[line 1] Error at 'let': Expected expression.` | Yes |
| Trailing expression token | `1 2` | At `2`: `Unexpected token after expression.` | `[line 1] Error at '2': Unexpected token after expression.` | Yes |
| Source-file mode | `test/lab3/precedence.vanta` | Status 0 and precedence AST | Status 0; `(or false (and true (== (+ 1 (* 2 3)) 7)))` | Yes |
| Source syntax error, no AST | `test/lab3/missing_right_paren.vanta` | Status 65, localized error, empty stdout | Status 65, expected error, empty stdout | Yes |
| Source lexical error, no AST | `1 + @ 2` | Status 65, unexpected-character error, empty stdout | `[line 1] Error: Unexpected character '@'.`; empty stdout | Yes |
| REPL recovery | Lines `1 +`, `@`, then `2 * 3` | Two errors, then `(* 2 3)` without restarting | Both errors reported; next prompt printed `(* 2 3)` | Yes |
| Legacy scanner mode | `--tokens test/lab1/operators.vanta` | Status 0 with token names and EOF | Output contains `LEFT_PAREN` through `EOF` | Yes |

Causes of the syntax errors:

- `1 +` reaches EOF where the right operand should begin.
- `+ 1` begins with a binary operator where a primary expression is required.
- `(1 + 2` reaches EOF before the grouping's required `)`.
- `1 + 2)` finishes a valid expression but leaves an unmatched `)` trailing.
- `let` is a statement keyword, not a valid primary expression in this grammar.
- `1 2` contains a second literal after the first expression is complete.

Automated results:

```text
Lab 1: Ran 16 tests - OK
Lab 2: Ran 6 tests - OK
Lab 3: Ran 16 tests - OK
```

## Grammar syntax tree and printed AST

For the valid expression `1 + 2 * 3`, this diagram follows the grammar's
nonterminals. The multiplication stays inside the second `factor`, below the
surrounding `term`, which gives `*` higher precedence than `+`.

```text
expression
└── logic_or
    └── logic_and
        └── equality
            └── comparison
                └── term
                    ├── factor
                    │   └── unary
                    │       └── primary
                    │           └── NUMBER 1
                    ├── "+"
                    └── factor
                        ├── unary
                        │   └── primary
                        │       └── NUMBER 2
                        ├── "*"
                        └── unary
                            └── primary
                                └── NUMBER 3
```

The program prints:

```text
(+ 1 (* 2 3))
```

The printed AST omits grammar-only wrapper levels but preserves the same semantic
tree: `+` is the root, `1` is its left child, and the `*` subtree is its right
child.

## Known limitations

- The parser accepts exactly one expression per file or interactive line.
- Variable references, assignment, function calls, declarations, and statements
  are not part of the Lab 3 expression grammar.
- The parser reports the first syntax error in an expression; it does not attempt
  multi-error recovery within that same expression.
- The REPL submits one physical line at a time, so file mode is needed for a
  multiline string or a grouping spread across lines.
- The AST is printed but not evaluated or executed.

All documented tests pass; there are no known failing Lab 3 tests. No optional
extra-credit claim is being made.
