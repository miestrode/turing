import functools
import gc
import glob
import json
import multiprocessing as mp
import os
import random
import shutil
import signal
import subprocess
import sys
import time

import stringcolor

REPORT_CARD_HEADER = "== REPORT CARD =="
SECOND_IN_MINUTE = 60

EXECUTION_TIMEOUT = 3
LEARNING_TIMEOUT = 0 * SECOND_IN_MINUTE
EXECUTIONS = 1

WORKERS = 1  # This should essentially be equivalent to the exploitable CPU cores assuming we want parallelness

MEMORY_LIMIT = 4  # Max memory for process in GB
KILOBYTE_LIMIT = MEMORY_LIMIT * 1000**2

TASK_COLOR = "#b0b0b0"

DOMAIN_FILENAME = "domain.pddl"
AGENT_FILENAME = "my_executive.py"
ROOT = os.path.abspath(".")
SANDBOX_FOLDER = "rundirs"
DOMAIN_FOLDER = "domains"
LOG_FOLDER = "logs"
AGENT_FOLDER = "agents"
AGENT_FILE = "my_executive.py"

PYTHON_COMMAND = "micromamba run -n 2 python"

WORKER_PRINTING_DATA = {}


# This should generate more bright and therefore usable colors
def random_color() -> str:
    red = random.randrange(100, 256)
    green = random.randrange(100, 256)
    blue = random.randrange(100, 256)

    return f"#{red:02X}{green:02X}{blue:02X}"


def clear_temps():
    for directory in glob.glob(os.path.join(ROOT, LOG_FOLDER, "*")):
        shutil.rmtree(directory)

    for directory in glob.glob(os.path.join(ROOT, SANDBOX_FOLDER, "*")):
        shutil.rmtree(directory)


def construct_log(
    agent_name: str,
    domain_name: str,
    problem_name: str,
    stdout: str,
    stderr: str,
    wall_time: float,
    learning: bool,
    terminated: str | None,
):
    base = {
        "agent": agent_name,
        "domain": domain_name,
        "problem": problem_name,
        "cpu-time": None,
        "wall-time": wall_time,
        "stderr": stderr,
        "success": False,
        "actions": None,
        "perception-requests": None,
        "learning": learning,
        "terminated": terminated,
    }

    if stdout and REPORT_CARD_HEADER in stdout:
        # With the current changes in pddlsim, there may be multiple return cards
        card: str = stdout.split(REPORT_CARD_HEADER)[-1]

        try:
            data = dict([tuple(line.split(": ")) for line in card.splitlines() if line])

            base.update(
                {
                    "actions": int(data["Total actions"]),
                    "perception-requests": int(data["Total perception requests"]),
                    "success": bool(data["Success"]),
                    "cpu-time": float(data["Total time"]),
                }
            )
        except (ValueError, KeyError):
            pass

    if learning:
        base["success"] = None

    return base


def copy_to_cwd(path_to_file: str):
    move_path = os.path.basename(path_to_file)
    shutil.copy(path_to_file, "./" + move_path)

    return move_path


def print_with_id(value):
    lines = value.splitlines()
    worker_id = mp.current_process().pid

    color, task = WORKER_PRINTING_DATA[worker_id]

    info_text = f"({worker_id})"

    print(stringcolor.cs(info_text, color), lines[0], stringcolor.cs(f"[{task}]", TASK_COLOR))

    for line in lines[1:]:
        print("|".rjust(len(info_text), " "), line)


def run_once(
    agent_path: str,
    domain_path: str,
    problem_path: str,
    learning: bool,
    agent_name: str,
    domain_name: str,
    problem_name: str,
):
    timeout = LEARNING_TIMEOUT if learning else EXECUTION_TIMEOUT

    wrapper = f"../../timeout -t {timeout} -m {KILOBYTE_LIMIT} -c --no-info-on-success"
    command = f"{wrapper} {PYTHON_COMMAND} {agent_path} {'-L' if learning else '-E'} {domain_path} {problem_path}"

    start = time.time()
    process = subprocess.run(command, capture_output=True, shell=True)
    wall_time = time.time() - start

    stdout = str(process.stdout, "utf-8")
    stderr = str(process.stderr, "utf-8")
    terminated = None

    match process.returncode:
        case 0 | 128:
            print_with_id("Ended run.")
        case 129:
            terminated = "timeout"
            print_with_id("Run failed due to a timeout.")
        case 130:
            terminated = "memory"
            print_with_id("Run failed due to overconsumption of memory.")
        case _:
            terminated = "internal"
            print_with_id(f"Run failed due to an internal agent error.\nBelow is the STDERR of the run:\n{stderr}")

    return construct_log(agent_name, domain_name, problem_name, stdout, stderr, wall_time, learning, terminated)


def run_task(agent_name: str, domain_name: str, problem_name: str, execution: None | int):
    learn_run_kind = "learn"
    run_kind = learn_run_kind if execution is None else f"run_{execution}"

    try:
        base_rundir = f"{agent_name}|{domain_name}|{problem_name}|"

        # Create a new sandbox for running this experiment and switch to it
        rundir = os.path.join(
            ROOT,
            SANDBOX_FOLDER,
            f"{base_rundir}{run_kind}",
            "",
        )

        if execution is not None:
            learning_rundir = os.path.join(ROOT, SANDBOX_FOLDER, f"{base_rundir}{learn_run_kind}", "")
            shutil.copytree(learning_rundir, rundir)  # This creates `rundir` so no need to use `mkdir`
        else:
            agent_directory = os.path.join(ROOT, AGENT_FOLDER, agent_name, "")
            shutil.copytree(agent_directory, rundir)  # This creates `rundir` so no need to use `mkdir`

        os.chdir(rundir)

        # Copy files into the rundir for sandboxing
        domain_path = copy_to_cwd(os.path.join(ROOT, DOMAIN_FOLDER, domain_name, DOMAIN_FILENAME))
        problem_path = copy_to_cwd(os.path.join(ROOT, DOMAIN_FOLDER, domain_name, f"{problem_name}.pddl"))

        # Initialize log directories
        log_directory = os.path.join(ROOT, LOG_FOLDER, agent_name, domain_name, problem_name, "")

        os.makedirs(log_directory, exist_ok=True)

        worker_id = mp.current_process().pid

        if worker_id not in WORKER_PRINTING_DATA:
            WORKER_PRINTING_DATA[worker_id] = [random_color(), None]

        WORKER_PRINTING_DATA[mp.current_process().pid][1] = f"{agent_name} on {problem_name}@{domain_name} ({run_kind})"

        print_with_id("Began run.")

        with open(os.path.join(log_directory, f"{run_kind}.json"), "w") as file:
            json.dump(
                run_once(
                    AGENT_FILE,
                    domain_path,
                    problem_path,
                    execution is None,
                    agent_name,
                    domain_name,
                    problem_name,
                ),
                file,
                indent=4,
            )

        if execution is not None:
            shutil.rmtree(rundir)
    except Exception as e:
        import traceback

        traceback.print_exception(e)
        print_with_id(f"Job suffered an internal error: [{e}].")
        raise e


def full_run(agents: list[str]):
    clear_temps()

    domains = {
        domain.split("/")[-2]: [
            os.path.basename(problem).split(".")[0]
            for problem in glob.glob(os.path.join(domain, "*.pddl"))
            if os.path.basename(problem) != "domain.pddl"
        ]
        for domain in glob.glob("domains/*/")
    }

    with mp.Pool(processes=WORKERS) as pool:
        results = []

        # Drain current tasks
        for agent_name in agents:
            for domain_name, problems in domains.items():
                for problem_name in problems:

                    def callback(ran_agent_name: str, ran_domain_name: str, ran_problem_name: str, _result):
                        for run_number in range(EXECUTIONS):
                            results.append(
                                pool.apply_async(
                                    run_task,
                                    [ran_agent_name, ran_domain_name, ran_problem_name, run_number],
                                )
                            )

                    results.append(
                        pool.apply_async(
                            run_task,
                            [agent_name, domain_name, problem_name, None],
                            callback=functools.partial(callback, agent_name, domain_name, problem_name),
                        )
                    )

        [result.wait() for result in results]


if __name__ == "__main__":
    os.setpgrp()  # Set all processes here as part of a process group

    try:
        full_run(sys.argv[1:])
    finally:
        gc.collect()
        os.killpg(0, signal.SIGTERM)  # Clean up things if necessary
