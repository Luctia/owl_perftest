import random

TERMINALS = ["number", "identifier", "integer", "string"]


def get_random_terminal():
    terminals = list(dict.fromkeys(random.choices(TERMINALS, k=random.randint(1, len(TERMINALS)))))
    output = terminals[0]
    for terminal in terminals[1:]:
        output += " | " + terminal
    return output


def many(N, filename):
    grammar = open(filename, "w")
    for i in range(N):
        grammar.write("a" + str(i) + " = " + get_random_terminal() + "\n")
    grammar.close()


def deep(N, filename):
    grammar = open(filename, "w")
    for i in range(N):
        grammar.write("a" + str(i) + " = a" + str(i + 1) + "\n")
    grammar.write("a" + str(N) + " = " + get_random_terminal())
    grammar.close()


def recursion(N, filename):
    grammar = open(filename, "w")
    token_pairs = [["{", "}"], ["(", ")"], ["[", "]"]]
    # First, we write a terminal that could be anything.
    res = "recurse0 = " + get_random_terminal() + "\n"
    for i in range(N):
        token_pair = random.choice(token_pairs)
        res = "recurse" + str(i + 1) + " = [ '" + token_pair[0] + "' recurse" + str(i) + " '" + token_pair[1] + "' ]\n" + res
    grammar.write(res)
    grammar.close()
    # At large N:
    # free(): invalid next size (fast)
    # Aborted (core dumped)


def conditionals(N, filename):
    grammar = open(filename, "w")
    output = get_random_terminal()
    terminals = ""
    # N = 331 is most we could get until Owl indicated that we were too deeply nested.
    if N > 331:
        N = 331
    for i in range(N):
        terminals += "terminal" + str(i * 2) + " = " + get_random_terminal() + "\n"
        terminals += "terminal" + str(i * 2 + 1) + " = " + get_random_terminal() + "\n"
        output = "(terminal" + str(i * 2) + " " + output + ")? terminal" + str(i * 2 + 1)
    grammar.write("if = " + output + "\n" + terminals)
    grammar.close()
