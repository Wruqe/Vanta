import sys

try:
    from .ast_printer import AstPrinter
    from .parser import Parser
    from .scanner import Scanner
except ImportError:  # running src/main.py directly
    from ast_printer import AstPrinter
    from parser import Parser
    from scanner import Scanner


USAGE = "Usage: python3 src/main.py [--tokens] [script.vanta]"


def run(source, output=None, error_output=None, tokens_only=False):
    output = sys.stdout if output is None else output
    error_output = sys.stderr if error_output is None else error_output

    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    if tokens_only:
        # handy for checking the older scanner lab
        for token in tokens:
            print(token, file=output)
    elif not scanner.errors:
        parser = Parser(tokens)
        expression = parser.parse()

        for line, location, message in parser.errors:
            print(f"[line {line}] Error {location}: {message}", file=error_output)

        if expression is not None:
            print(AstPrinter().print(expression), file=output)

        if parser.errors:
            return False

    # lexical mess means no AST
    for line, message in scanner.errors:
        print(f"[line {line}] Error: {message}", file=error_output)

    return not scanner.errors


def run_file(path, tokens_only=False):
    try:
        with open(path, encoding="utf-8") as source_file:
            source = source_file.read()
    except OSError as error:
        print(f"Could not read {path!r}: {error}", file=sys.stderr)
        return 74

    return 0 if run(source, tokens_only=tokens_only) else 65


def run_prompt(tokens_only=False):
    while True:
        try:
            # fresh scanner and parser for every line
            source = input("Vanta > ")
        except EOFError:
            print()
            return 0
        except KeyboardInterrupt:
            print()
            return 130

        run(source, tokens_only=tokens_only)


def main(arguments=None):
    arguments = list(sys.argv[1:] if arguments is None else arguments)
    tokens_only = False

    if arguments and arguments[0] == "--tokens":
        tokens_only = True
        arguments.pop(0)

    if len(arguments) > 1 or (arguments and arguments[0].startswith("--")):
        print(USAGE, file=sys.stderr)
        return 64
    if arguments:
        return run_file(arguments[0], tokens_only=tokens_only)
    return run_prompt(tokens_only=tokens_only)


if __name__ == "__main__":
    raise SystemExit(main())
