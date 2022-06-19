import json
import os
import re
import shutil
import subprocess
import time
# import tracemalloc
from subprocess import call
import grammar_generator
import numpy as np
import matplotlib.pyplot as plt


TYPES = ["recursion", "long", "deep"]


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


def generate_linear_graph(data, grammar_type):
    x = np.linspace(0, int(max([int(key) for key in data.keys()])), int(len(data)))
    time_to_generate = [info['time'] for info in data.values()]
    lines = [info['lines'] for info in data.values()]

    fig, ax1 = plt.subplots()
    ax1.plot(x, time_to_generate)

    ax1.set(xlabel='length of grammar', ylabel='time (s)')
    ax1.grid()

    ax2 = ax1.twinx()
    ax2.plot(x, lines, color='r')
    ax2.set_ylabel("# of lines")
    ax2.tick_params(axis='y', labelcolor='r')

    fig.tight_layout()

    plt.savefig(grammar_type + '.png')
    plt.clf()


def generate_polynomial_graph(data, grammar_type):
    x = [int(key) for key in data.keys()]
    time_to_generate = [info['time'] for info in data.values()]
    lines = [info['lines'] for info in data.values()]

    fig, ax1 = plt.subplots()
    fit = np.polyfit(x, np.log(time_to_generate), 1)
    a = np.exp(fit[1])
    b = fit[0]
    x_fitted = np.linspace(np.min(x), np.max(x), len(lines))
    ttg_fitted = a * np.exp(b * x_fitted)
    ax1.plot(x_fitted, ttg_fitted)
    ax1.scatter(x_fitted, ttg_fitted, c=[], edgecolors='#cccccc', s=50, cmap='Dark2')
    ax1.set(xlabel='length of grammar', ylabel='time (s)')
    ax1.grid()

    ax2 = ax1.twinx()
    ax2.plot(x_fitted, lines, color='r')
    ax2.set_ylabel("# of lines")
    ax2.tick_params(axis='y', labelcolor='r')

    fig.tight_layout()

    plt.savefig(grammar_type + '.png')
    plt.clf()


def generate_graphs():
    print("Generating graphs...")
    files = os.listdir(".")
    result_files = [file for file in files if file.__contains__("_results.json")]
    progress_bar(0, len(result_files))
    for i, file in enumerate(result_files):
        grammar_type = file.split('_')[0]
        if grammar_type == "deep" or grammar_type == "recursion":
            # We noticed that for this grammar, Owl takes exponential time to generate parsers.
            generate_polynomial_graph(json.load(open(file)), grammar_type)
        else:
            generate_linear_graph(json.load(open(file)), grammar_type)
        progress_bar(i + 1, len(result_files))
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
    generate_grammars(80, step_size=1)
    run_generating_tests()
    add_line_counts()
    generate_graphs()
    # If we're not interested in the output of Owl, we remove all the parsers and tests after running.
    shutil.rmtree('parsers', ignore_errors=True)
    shutil.rmtree('tests', ignore_errors=True)
