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


TYPES = ["long"]
# TYPES = ["long", "deep", "stacked", "declaration", "mixed"]


def progress_bar(progress, total):
    percent = 100 * (progress / float(total))
    bar = '█' * int(percent) + '-' * int(100 - percent)
    print(f"\r|{bar}| {percent:.2f}%", end="\r")


def generate_grammars(N, step_size=50):
    print("Generating grammars...")
    progress_bar(0, N * len(TYPES))
    for i, type in enumerate(TYPES):
        generator = getattr(grammar_generator, type)
        for j in range(N):
            generator(step_size*j + 1, "tests/" + type + "_" + str(step_size*j) + ".owl")
            progress_bar(j + 1 + N * i, N * len(TYPES))
    print("\nDone.")


def run_generating_tests():
    files = os.listdir("tests")
    for type in TYPES:
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
    time_to_generate = [info['time'] for info in data.values()]
    lines = [info['lines'] for info in data.values()]

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

    fig, ax1 = plt.subplots()
    ax1.plot(x, time_to_generate)

    ax1.set(xlabel='length of grammar', ylabel='time (s)',
           title='Time to generate a parser for a ' + grammar_type + ' grammar of a certain length')
    ax1.grid()

    ax2 = ax1.twinx()
    ax2.plot(x, lines)

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
    files = os.listdir(os.getcwd() + "/parsers/")
    progress_bar(0, len(files))
    processed = 0
    for type in TYPES:
        type_files = [file for file in files if file.__contains__(type)]
        current_data = json.load(open(os.getcwd() + "/" + type + "_results.json"))
        for file in type_files:
            with open(os.getcwd() + "/parsers/" + file, "r") as parser:
                # Read all lines that aren't comments or empty
                content = parser.read()
                lines = len(re.findall(r"\n[^/\n]", content))
                parser.close()
            current_data[file.split('_')[1][:-2]]['lines'] = lines
            processed += 1
            progress_bar(processed, len(files))
        json.dump({int(entry): current_data[entry] for entry in current_data.keys()}, open(os.getcwd() + "/" + type + "_results.json", "w"), sort_keys=True, indent=4)
    progress_bar(1, 1)
    print("\nDone.")


if __name__ == '__main__':
    if not os.path.isdir(os.getcwd() + "/tests/"):
        os.mkdir("tests")
    if not os.path.isdir(os.getcwd() + "/parsers/"):
        os.mkdir("parsers")
    generate_grammars(500, step_size=5)
    run_generating_tests()
    add_line_counts()
    generate_graphs()
