# Vanta Lab 1: Lexical Scanner

## Language

The language is named **Vanta**. Lab 1 implements only Vanta's lexical scanner. It
reads source text and produces tokens; it does not parse, evaluate, or execute the
program.

## Lexical grammar

The descriptions below match the scanner implementation.

### Identifier

```text
[A-Za-z_][A-Za-z0-9_]*
```

Identifiers use ASCII letters and underscore for the first character. Later
characters may also contain ASCII digits. After consuming the complete identifier,
the scanner checks whether it exactly matches a keyword.

### Number

```text
[0-9]+(\.[0-9]+)?
```

A number contains one or more digits and may have one fractional part. The decimal
point is part of the number only when at least one digit follows it. Integers become
Python `int` values and decimals become Python `float` values.

### String

```text
"([^"\\]|\\["\\nrt])*"
```

In this notation, the contents may include newlines. The scanner stores the full
quoted source as the token's lexeme and the text between the quotes as its literal
value. Newlines inside a string update the line counter. Backslash escape sequences
`\"`, `\\`, `\n`, `\r`, and `\t` are interpreted in the literal value. Any other
escape sequence is reported as a lexical error.

## Design choices

Vanta reserves these keywords:

```text
let fn if else while for return true false null print and or
```

`true` and `false` carry the Python literal values `True` and `False`; `null` carries
`None`. Operators are `+`, `-`, `*`, `/`, `!`, `!=`, `=`, `==`, `<`, `<=`, `>`, and
`>=`. Punctuation is `(`, `)`, `{`, `}`, `,`, `.`, and `;`.

`and` and `or` are reserved as word-based logical operators. They follow Lox's
logical-expression grammar and avoid adding symbolic `&&` and `||` spellings for
the same operations.

Spaces, tabs, and carriage returns are ignored. A newline increments the current
line. `//` starts a comment that continues to the next newline, while a single `/`
is a division token. Unexpected characters, invalid string escapes, and unterminated
strings are collected as lexical errors with line numbers. Scanning continues after
an unexpected character or invalid escape.

The design follows the scanner in *Crafting Interpreters*, but differs from Lox by
using `let`, `fn`, `null`, and `print` as Vanta keywords and representing whole
numbers as Python integers rather than converting every number to a floating-point
value. Vanta retains Lox's `and` and `or` because they are required for logical
expressions, but omits the object-oriented `class`, `super`, and `this` keywords;
the current Vanta grammar defines no class syntax, so reserving those words would
unnecessarily prevent their use as identifiers. They can be reserved if class
syntax is added later.

Every produced `Token` contains a token type, the original lexeme, a literal value
(or `None` when not applicable), and a line number. An EOF token is always appended.

## Setup and execution

No third-party packages are required. Run all commands from the repository root
with Python 3.

Scan a source file:

```bash
python3 src/main.py test/lab1/basic.vanta
```

Start interactive mode:

```bash
python3 src/main.py
```

The interactive prompt is `Vanta > `. Send EOF (`Ctrl-D` on macOS/Linux) to exit.
A lexical error is printed to standard error and the next prompt is still shown.

Run the complete automated test suite:

```bash
python3 -m unittest discover -s test/lab1 -p 'test_*.py' -v
```

Optional individual fixture runs:

```bash
python3 src/main.py test/lab1/operators.vanta
python3 src/main.py test/lab1/literals.vanta
python3 src/main.py test/lab1/comments.vanta
python3 src/main.py test/lab1/errors.vanta
```

A file containing lexical errors exits with status 65. An unreadable file exits
with status 74, and an invalid number of command-line arguments exits with status
64.

## Test results

The following results were reproduced on October 2, 2026. Token lists below are the
actual token-type sequences checked by the automated tests. Literal and line values
listed in the results are also exact assertions.

| Purpose | Source input | Expected tokens or errors | Actual output | Match |
|---|---|---|---|---|
| Punctuation | `(){} ,.;` | `LEFT_PAREN RIGHT_PAREN LEFT_BRACE RIGHT_BRACE COMMA DOT SEMICOLON EOF` | Same sequence | Yes |
| Arithmetic and comparison operators | `+ - * / ! != = == < <= > >=` | `PLUS MINUS STAR SLASH BANG BANG_EQUAL EQUAL EQUAL_EQUAL LESS LESS_EQUAL GREATER GREATER_EQUAL EOF` | Same sequence | Yes |
| All keywords | `let fn if else while for return true false null print and or` | `LET FN IF ELSE WHILE FOR RETURN TRUE FALSE NULL PRINT AND OR EOF`; literals `True`, `False`, `None` | Same sequence and literals | Yes |
| Identifiers | `alpha _private name2 letdown` | Four `IDENTIFIER` tokens followed by `EOF`; complete lexemes preserved | Same sequence; lexemes `alpha`, `_private`, `name2`, `letdown` | Yes |
| Integers, decimals, and dot boundary | `10 123 3.14 0.5 1.foo` | `NUMBER NUMBER NUMBER NUMBER NUMBER DOT IDENTIFIER EOF`; literals `10`, `123`, `3.14`, `0.5`, `1` | Same sequence and literals | Yes |
| Strings and multiline tracking | `"hello world" "line one<newline>line two" next` | `STRING STRING IDENTIFIER EOF`; unquoted string literals; lines `1, 2, 2, 2` | Same sequence, literals, and lines | Yes |
| String escapes | `"quote: \" slash: \\ newline: \n tab: \t"` | `STRING EOF`; literal contains decoded quote, backslash, newline, and tab characters | Same sequence and literal | Yes |
| Invalid string escape | `"bad\q" let` | Error `[line 1] Invalid escape sequence '\q'.`; scan continues with `STRING LET EOF` | Same error and tokens | Yes |
| Comment, whitespace, newline, slash, and EOF | `let // ignored<CR><newline><tab>name / 2` | `LET IDENTIFIER SLASH NUMBER EOF`; lines `1, 2, 2, 2, 2`; empty EOF lexeme | Same sequence, lines, and EOF lexeme | Yes |
| Unterminated string | `"not closed` | Error `[line 1] Unterminated string.` and `EOF` | Same error tuple and token | Yes |
| Unexpected character recovery | `@ let` | Error `[line 1] Unexpected character '@'.`; then `LET EOF` | Same error and tokens | Yes |
| Larger Vanta program | `test/lab1/basic.vanta` | No errors; begins with `FN`, includes `GREATER_EQUAL` and `STRING`, ends with `EOF` | All assertions satisfied | Yes |
| Source-file mode | `python3 src/main.py test/lab1/basic.vanta` | Status 0; output contains `FN`, `STRING`, and `EOF`; no stderr | Status 0 with expected output and empty stderr | Yes |
| Erroneous source-file mode | `python3 src/main.py test/lab1/errors.vanta` | Status 65; both unexpected-character and unterminated-string errors | Status 65 with both errors | Yes |
| Interactive error recovery | Input `@<newline>let ok = 1;<newline>` | Status 0 at EOF; error reported; next line produces `LET`, `IDENTIFIER`, and another `EOF` | Prompt continued and all expected output appeared | Yes |
| Invalid CLI arguments | `python3 src/main.py one.vanta two.vanta` | Status 64 and usage text | Status 64 with usage text | Yes |

Automated suite result:

```text
Ran 16 tests in 0.110s

OK
```

An additional syntax check also succeeded:

```bash
python3 -m py_compile src/token_type.py src/vanta_token.py src/scanner.py src/main.py
```

## Known limitations

- Strings support a deliberately small escape set (`\"`, `\\`, `\n`, `\r`, and
  `\t`) rather than arbitrary or Unicode escape forms.
- Identifiers are deliberately ASCII-only, matching the documented grammar.
- Numbers do not support exponents, leading-dot forms such as `.5`, trailing-dot
  forms such as `1.`, or numeric separators.
- File input supports multiline strings. The REPL scans each submitted line
  independently, so an interactive string must close on the same submitted line.
- This lab ends after tokenization. There is intentionally no parser, AST,
  evaluator, or execution stage.

All documented tests pass; there are no known failing Lab 1 tests.
