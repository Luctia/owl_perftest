import random

TERMINALS = ["number", "identifier", "integer", "string"]


def get_random_terminal():
    return random.choice(TERMINALS)


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


def stacked(N, filename):
    pass


def declaration(N, filename):
    pass


def mixed(N, filename):
    pass
