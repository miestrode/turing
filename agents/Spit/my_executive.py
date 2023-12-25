from __future__ import division
import json
import sys
from executives import LearnedExecutor, Q_Learner
from local_simulator import LocalSimulator
import time
from multiprocessing import Process, Queue, cpu_count
import collections
import numpy as np
import random


#####################
# T value functions:


def t1(temp_t):
    if (temp_t) <= 1:
        return 1
    else:
        return (temp_t/2*(np.sin(temp_t/4) + 1)) / 30 + 1


def t2(temp_t):
    if temp_t <= 1:
        return 1
    else:
        return (temp_t/2*(np.cos(temp_t/2) + 1)) / 30 + 1


def t3(temp_t):
    if temp_t <= 1:
        return 1
    else:
        return (temp_t/2*(np.sin(temp_t/5) + 1)) / 20 + 1


def t4(temp_t):
    if temp_t <= 1:
        return 1
    else:
        return (temp_t/2*(np.sin(temp_t/2) + 1)) / 20 + 1


def t5(temp_t):
    if temp_t <= 1:
        return 1
    else:
        return (temp_t/2*(np.sin(temp_t/2) + 1)) / 30 + 1


def t6(temp_t):
    if temp_t <= 1:
        return 1
    else:
        return (temp_t/2*(np.cos(temp_t/5) + 1)) / 20 + 1


def t7(temp_t):
    if temp_t <= 14:
        return 1
    else:
        return np.sqrt(temp_t)*np.log10(temp_t) / 8


def t8(temp_t):
    if temp_t <= 7:
        return 1
    else:
        return np.sqrt(temp_t)*np.log10(temp_t) / 5


def run_multiple_agents():
    table_queue = Queue()
    LocalSimulator(print_actions=False).run(sys.argv[2], sys.argv[3], Q_Learner(0, table_queue, random.randint(1500, 3000), t1))
    average_results(table_queue, agents)


def average_results(queue, agents):
    for agent in agents:
        agent.terminate()
    time.sleep(5)
    average = collections.defaultdict(dict)
    div = 1 / queue.qsize()
    table = json.loads(queue.get())
    file_name = table["name"][:-1] + "final"
    average["files"] = [table["name"]]
    while not queue.empty():
        print "parsing table"
        states = [state for state in table.keys() if (state != "mode" and state != "name")]
        for state in states:
            for action in table[state]:
                if action in average[state].keys():
                    average[state][action] += table[state][action] * div
                else:
                    average[state][action] = table[state][action] * div
        average["files"].append(table["name"])
        table = json.loads(queue.get())
    with open(file_name, 'w') as outfile:
        json.dump(average, outfile)
    outfile.close()


if __name__ == '__main__':
    # learning modes
    if sys.argv[1] == "-L":
        run_multiple_agents()
    # executing mode
    elif sys.argv[1] == "-E":
        print LocalSimulator().run(sys.argv[2], sys.argv[3], LearnedExecutor())
    else:
        print "wrong arguments for main"
        exit(1)
