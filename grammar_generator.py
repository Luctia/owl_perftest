def long(N, filename):
    pass


def deep(N, filename):
    grammar = open(filename, "w")
    for i in range(N):
        grammar.write("a" + str(i) + " = a" + str(i + 1) + "\n")
    grammar.write("a" + str(N) + " = number")


def stacked(N, filename):
    pass


def declaration(N, filename):
    pass


def mixed(N, filename):
    pass
