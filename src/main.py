import sys

try:
    from .scanner import Scanner
except ImportError:  # Support running src/main.py directly.
    from scanner import Scanner


USAGE = "Usage: python src/main.py [script.vanta]"


def run(source, output=sys.stdout, error_output=sys.stderr):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    # show whatever the scanner managed to find
    for token in tokens:
        print(token, file=output)

    for line, message in scanner.errors:
        print(f"[line {line}] Error: {message}", file=error_output)

    return not scanner.errors


def run_file(path):
    try:
        with open(path, encoding="utf-8") as source_file:
            source = source_file.read()
    except OSError as error:
        print(f"Could not read {path!r}: {error}", file=sys.stderr)
        return 74

    return 0 if run(source) else 65


def run_prompt():
    while True:
        try:
            # each prompt line gets a fresh scanner
            source = input("Vanta > ")
        except EOFError:
            print()
            return 0
        except KeyboardInterrupt:
            print()
            return 130

        run(source)


def main(arguments=None):
    arguments = sys.argv[1:] if arguments is None else arguments

    if len(arguments) > 1:
        print(USAGE, file=sys.stderr)
        return 64
    if len(arguments) == 1:
        return run_file(arguments[0])
    return run_prompt()


if __name__ == "__main__":
    raise SystemExit(main())
