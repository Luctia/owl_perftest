import json
import os
import re
import time
# import tracemalloc
import grammar_generator


def generate_grammars():
    N = 2
    for i in range(11):
        grammar_generator.deep(N**i, "tests/deep_" + str(N**i) + ".owl")


def run_generating_tests():
    types = ["long", "deep", "stacked", "declaration", "mixed"]
    files = os.listdir("tests")
    for type in ["deep"]:
        results = dict()
        type_files = [file for file in files if file.__contains__(type)]
        # tracemalloc.start()
        for file in type_files:
            start = time.time()
            os.system("owl -c " + os.getcwd() + "/tests/" + file + " -o /dev/null")
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


if __name__ == '__main__':
    if not os.path.isdir(os.getcwd() + "/tests/"):
        os.mkdir("tests")
    generate_grammars()
    run_generating_tests()
