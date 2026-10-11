# Vanta Lab 2: AST Printer

## Expression grammar

Vanta uses the following expression grammar. Rules are ordered from lowest to
highest precedence.

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

The literal types are integer, decimal, string, Boolean, and null. Binary
operators are `or`, `and`, `!=`, `==`, `>`, `>=`, `<`, `<=`, `-`, `+`, `/`, and
`*`. Unary operators are `!` and `-`.

## AST design

The implementation defines an abstract `Expr` base class and four concrete
expression classes:

- `Binary(left, operator, right)` stores two operands and their operator.
- `Unary(operator, right)` stores an operator and its operand.
- `Grouping(expression)` preserves explicit parentheses.
- `Literal(value)` stores an integer, float, string, Boolean, or `None`.

Each class implements `accept()` for visitor dispatch. `AstPrinter` is the first
visitor: it prints an operator followed by its child expressions inside
parentheses, making tree hierarchy explicit. Strings use escaped double quotes so
they remain visibly different from operator names. Booleans and null use Vanta's
source spellings: `true`, `false`, and `null`.

Vanta follows Lox's expression structure, but it keeps integer literals as Python
`int` values, uses `null` rather than `nil`, and includes the word operators `and`
and `or` already introduced by Vanta's scanner. The logical operators use the same
`Binary` representation as the other two-operand expressions; a separate logical
node would store the same three fields and is unnecessary before evaluation.

## Setup and execution

No third-party dependencies are required. Run these commands from the repository
root with Python 3.

Print the three hard-coded AST examples:

```bash
python3 test/lab2/ast_examples.py
```

Run the Lab 2 automated tests:

```bash
python3 -m unittest discover -s test/lab2 -p 'test_*.py' -v
```

Run both lab suites:

```bash
python3 -m unittest discover -s test/lab1 -p 'test_*.py' -v
python3 -m unittest discover -s test/lab2 -p 'test_*.py' -v
```

## Test cases and results

The following results were reproduced on October 10, 2026. In the abbreviated
constructor notation below, quoted operator text stands for the corresponding
`Token` object used by the hard-coded Python tree.

### 1. Nested arithmetic

Purpose: exercise `Binary`, `Unary`, `Grouping`, and `Literal`; cover all four
arithmetic operators; cover integer and decimal literals; and verify nested
hierarchy.

Hard-coded AST:

```text
Binary(
  Unary("-", Literal(123)),
  "*",
  Grouping(
    Binary(
      Binary(Literal(45.67), "+", Binary(Literal(8), "/", Literal(2))),
      "-",
      Literal(1)
    )
  )
)
```

Expected output:

```text
(* (- 123) (group (- (+ 45.67 (/ 8 2)) 1)))
```

Actual output:

```text
(* (- 123) (group (- (+ 45.67 (/ 8 2)) 1)))
```

Match: Yes.

### 2. Comparison and equality tree

Purpose: cover `!=`, `==`, `>`, `>=`, `<`, and `<=`; verify string rendering; and
exercise deeply nested binary expressions. The full constructor calls are in
`test/lab2/ast_examples.py`; the tree is summarized here without the repeated
`Token(...)` wrappers.

Hard-coded AST:

```text
Binary(
  Binary(Binary(Literal("alpha"), "!=", Literal("beta")), "and",
         Binary(Literal(10), ">=", Literal(5))),
  "and",
  Binary(Binary(Binary(Literal(3), "<", Literal(4)), "==", Literal(true)),
         "and",
         Binary(Binary(Literal(6), ">", Literal(2)), "==",
                Binary(Literal(7), "<=", Literal(7))))
)
```

Expected output:

```text
(and (and (!= "alpha" "beta") (>= 10 5)) (and (== (< 3 4) true) (== (> 6 2) (<= 7 7))))
```

Actual output:

```text
(and (and (!= "alpha" "beta") (>= 10 5)) (and (== (< 3 4) true) (== (> 6 2) (<= 7 7))))
```

Match: Yes.

### 3. Logical and null tree

Purpose: cover `and`, `or`, unary `!`, Boolean literals, null literals, and another
nested equality expression.

Hard-coded AST:

```text
Binary(
  Binary(Literal(true), "and", Unary("!", Literal(false))),
  "or",
  Binary(Literal(null), "==", Literal(null))
)
```

Expected output:

```text
(or (and true (! false)) (== null null))
```

Actual output:

```text
(or (and true (! false)) (== null null))
```

Match: Yes.

The automated suite also verifies that the examples collectively contain every
expression class, operator, and literal type in the grammar. It checks that nodes
retain their required fields and that strings containing newlines and quotes are
escaped unambiguously.

## Known limitations

- The trees are constructed directly in Python because parsing is outside Lab 2.
- The printer represents tree structure only; it does not type-check or evaluate
  expressions.
- Vanta currently has no variable or assignment expression nodes because those
  forms are outside the required Lab 2 expression grammar.

All documented Lab 2 tests pass; there are no known failing tests.
