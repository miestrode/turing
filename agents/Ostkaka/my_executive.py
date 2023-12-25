import sys
from learning_manager import LearningManager
from executer_manager import ExecuterManager
from pddlsim.local_simulator import LocalSimulator

# Getting input from user
mode_arg = sys.argv[1]
domain_path = sys.argv[2]
problem_path = sys.argv[3]

if mode_arg == '-L':
    print LocalSimulator(print_actions=False).run(domain_path, problem_path, LearningManager())
elif mode_arg == '-E':
    print LocalSimulator().run(domain_path, problem_path, ExecuterManager())
else:
    print "Bad mode (should be '-L' or 'E')"
    exit()
