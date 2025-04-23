import difflib

def flat_map(f, xs):
    ys = []
    for x in xs:
        ys.extend(f(x))
    return ys

def pretty_print_diff(old, new):
    diff = difflib.ndiff(old.splitlines(), new.splitlines())
    for line in diff:
        if line.startswith("+"):
            print(f"\033[92m{line}\033[0m")
        elif line.startswith("-"):
            print(f"\033[91m{line}\033[0m")
        else:
            print(line)
