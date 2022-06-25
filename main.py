import json
import os
import re
import resource
import shutil
import subprocess
import time
from queue import Queue
from subprocess import call
from threading import Thread
import grammar_generator
import numpy as np
import matplotlib.pyplot as plt
from progress_bar import ProgressBar


TOTAL_MEMORY_GB = 50
TOTAL_WORKER_COUNT = 6
TYPES = ["long", "many", "optionals", "deep", "recursion"]
TEST_COUNT = 1000
STEP_SIZE = 10
REMOVE_AFTERWARDS = False


def progress_bar(progress, total):
    percent = 100 * (progress / float(total))
    bar = '█' * int(percent) + '-' * int(100 - percent)
    print(f"\r|{bar}| {percent:.2f}%", end="\r")


def generate_grammars():
    print("Generating grammars...")
    progress_bar(0, TEST_COUNT * len(TYPES))
    for i, type in enumerate(TYPES):
        generator = getattr(grammar_generator, type)
        for j in range(TEST_COUNT):
            generator(STEP_SIZE*j + 1, "tests/" + type + "_" + str(STEP_SIZE*j) + ".owl")
            progress_bar(j + 1 + TEST_COUNT * i, TEST_COUNT * len(TYPES))
    print("\nDone.")


def run_generating_tests():
    files = os.listdir("tests")
    for type in TYPES:
        print("Running generating tests for " + type + " grammars...")
        type_files = [file for file in files if file.__contains__(type)]
        bar = ProgressBar(len(type_files))
        thread_pool = [None] * len(type_files)
        results = dict()
        jobs = Queue()
        for i, file in enumerate(type_files):
            jobs.put(file)
        for _ in range(TOTAL_WORKER_COUNT):
            thread = Thread(target=worker, args=[results, bar, jobs])
            thread.setDaemon(True)
            thread.start()
        jobs.join()
        with open(os.getcwd() + "/" + type + "_results.json", "w") as res_file:
            json.dump(results, res_file, sort_keys=True, indent=4)
        bar.finish()
        print("\nDone.")


def worker(results, bar, jobs):
    resource.setrlimit(resource.RLIMIT_AS, (int((TOTAL_MEMORY_GB * 1000000000) / TOTAL_WORKER_COUNT), int((TOTAL_MEMORY_GB * 1073741824 * 10) / TOTAL_WORKER_COUNT)))
    while True:
        file = jobs.get()
        start = time.time()
        call("owl -c " + os.getcwd() + "/tests/" + file + " -o " + os.getcwd() + "/parsers/" + file[:-3] + "h", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        end = time.time()
        results[int(re.compile("(\d+)").search(file).groups(0)[0])] = {
                    "time": (end - start)
                }
        bar.done_with_step()
        jobs.task_done()


def generate_linear_graph(data, grammar_type):
    x = np.linspace(0, int(max([int(key) for key in data.keys()])), int(len(data)))
    time_to_generate = [info['time'] for info in data.values()]
    lines = [info['lines'] for info in data.values()]

    fig, ax1 = plt.subplots()
    ax1.plot(x, time_to_generate, label="Time")

    ax1.set(xlabel='length of grammar', ylabel='time (s)')
    ax1.grid()

    ax2 = ax1.twinx()
    ax2.plot(x, lines, color='r', label="# of lines")
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
    ax1.scatter(x_fitted, time_to_generate, c=[], edgecolors='#cccccc', s=50, cmap='Dark2')
    ax1.set(xlabel='length of grammar', ylabel='time (s)')
    ax1.grid()
    ax1.legend()

    ax2 = ax1.twinx()
    ax2.plot(x_fitted, lines, color='r')
    ax2.set_ylabel("# of lines")
    ax2.tick_params(axis='y', labelcolor='r')
    ax2.legend()

    fig.tight_layout()

    plt.savefig(grammar_type + '.png')
    plt.clf()


def generate_comparative_graphs(result_files_names):
    data = dict()
    for file in result_files_names:
        data[file.split('_')[0]] = json.load(open(file))
    lengths = []
    for type in data.keys():
        lengths.append(len(data[type]))
    x = [int(key) for key in data[list(data.keys())[0]]]
    # One graph for line counts
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 5, forward=True)
    for type in data.keys():
        lines = [data[type][point]['lines'] for point in data[type]]
        ax.plot([int(key) for key in data[type]], lines, label=type)
        ax.legend()
    ax.set_ylabel("# of lines")
    ax.set_xlabel("Size of grammar")
    ax.grid()
    fig.tight_layout()
    plt.savefig("line_compare.png")
    plt.clf()

    # Now onto comparing the times
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 5, forward=True)
    for i, type in enumerate(data.keys()):
        times = [data[type][point]['time'] for point in data[type]]
        ax.plot([int(key) for key in data[type]], times, label=type)
        ax.legend()
    ax.set_ylabel("Time to generate (s)")
    ax.set_xlabel("Size of grammar")
    ax.grid()
    fig.tight_layout()
    plt.savefig("time_compare_zoom.png")
    plt.clf()


def generate_graphs():
    print("Generating graphs...")
    files = os.listdir(".")
    result_files = [file for file in files if file.__contains__("_results.json")]
    progress_bar(0, len(result_files) + 2)
    for i, file in enumerate(result_files):
        grammar_type = file.split('_')[0]
        generate_linear_graph(json.load(open(file)), grammar_type)
        progress_bar(i + 1, len(result_files) + 2)
    generate_comparative_graphs(result_files)
    progress_bar(1, 1)
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
    generate_grammars()
    run_generating_tests()
    add_line_counts()
    generate_graphs()
    # If we're not interested in the output of Owl, we remove all the parsers and tests after running.
    if REMOVE_AFTERWARDS:
        shutil.rmtree('parsers', ignore_errors=True)
        shutil.rmtree('tests', ignore_errors=True)
