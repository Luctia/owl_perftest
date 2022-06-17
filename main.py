import json
import os
import re
import subprocess
import time
# import tracemalloc
from subprocess import call
import grammar_generator
import numpy as np
import matplotlib.pyplot as plt


def progress_bar(progress, total):
    percent = 100 * (progress / float(total))
    bar = '█' * int(percent) + '-' * int(100 - percent)
    print(f"\r|{bar}| {percent:.2f}%", end="\r")


def generate_grammars(N, step_size=50):
    print("Generating grammars...")
    progress_bar(0, N)
    for i in range(N):
        progress_bar(i + 1, N)
        grammar_generator.deep(step_size*i, "tests/deep_" + str(step_size*i) + ".owl")
    print("\nDone.")


def run_generating_tests():
    types = ["long", "deep", "stacked", "declaration", "mixed"]
    files = os.listdir("tests")
    for type in ["deep"]:
        print("Running generating tests for " + type + " grammars...")
        results = dict()
        type_files = [file for file in files if file.__contains__(type)]
        # tracemalloc.start()
        progress_bar(0, len(type_files))
        for i, file in enumerate(type_files):
            progress_bar(i + 1, len(type_files))
            start = time.time()
            call("owl -c " + os.getcwd() + "/tests/" + file + " -o " + os.getcwd() + "/parsers/" + file[:-3] + "h", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            # os.system("owl -c /home/luctia/PycharmProjects/OwlPerfTest/tests/" + file + " -o /dev/null")
            end = time.time()
            # mem_info = tracemalloc.get_traced_memory()
            results[int(re.compile("(\d+)").search(file).groups(0)[0])] = {
                "time": (end - start),
                # "memUsage": {
                #     "size": mem_info[0],
                #     "peak": mem_info[1]
                # }
            }
            # tracemalloc.clear_traces()
            # tracemalloc.reset_peak()
        # tracemalloc.stop()
        with open(os.getcwd() + "/" + type + "_results.json", "w") as res_file:
            json.dump(results, res_file, sort_keys=True, indent=4)
        print("\nDone.")


def generate_graph(data, grammar_type):
    x = np.linspace(0, int(max([int(key) for key in data.keys()])), int(len(data)))
    y = [time['time'] for time in data.values()]

    # fit a linear curve an estimate its y-values and their error.
    # a, b = np.polyfit(x, y, deg=1)
    # y_est = a * x + b
    # y_err = x.std() * np.sqrt(1 / len(x) +
    #                           (x - x.mean()) ** 2 / np.sum((x - x.mean()) ** 2))
    #
    # fig, ax = plt.subplots()
    # ax.plot(x, y_est, '-')
    # ax.fill_between(x, y_est - y_err, y_est + y_err, alpha=0.2)
    # ax.plot(x, y, 'o', color='tab:brown')

    fig, ax = plt.subplots()
    ax.plot(x, y)

    ax.set(xlabel='length of grammar', ylabel='time (s)',
           title='Time to generate a parser for a ' + grammar_type + ' grammar of a certain length')
    ax.grid()

    plt.savefig(grammar_type + '.png')


def generate_graphs():
    print("Generating graphs...")
    files = os.listdir(".")
    result_files = [file for file in files if file.__contains__("_results.json")]
    progress_bar(0, len(result_files))
    for i, file in enumerate(result_files):
        progress_bar(i + 1, len(result_files))
        generate_graph(json.load(open(file)), file.split('_')[0])
    print("\nDone")


def add_line_counts():
    print("Couting lines...")


if __name__ == '__main__':
    if not os.path.isdir(os.getcwd() + "/tests/"):
        os.mkdir("tests")
    if not os.path.isdir(os.getcwd() + "/parsers/"):
        os.mkdir("parsers")
    generate_grammars(5, step_size=20)
    run_generating_tests()
    generate_graphs()
