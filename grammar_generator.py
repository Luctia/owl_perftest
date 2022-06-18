import random

TERMINALS = ["number", "identifier", "integer", "string"]


def get_random_terminal():
    terminals = list(dict.fromkeys(random.choices(TERMINALS, k=random.randint(1, len(TERMINALS)))))
    output = terminals[0]
    for terminal in terminals[1:]:
        output += " | " + terminal
    return output


def long(N, filename):
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
    pass
    # grammar = open(filename, "w")
    # token_pairs = [["{", "}"], ["(", ")"], ["[", "]"]]
    # First, we write a terminal that could be anything.
    # for i in range(N):
    #
    # grammar.close()


def stacked(N, filename):
    pass


def declaration(N, filename):
    pass


def mixed(N, filename):
    pass
