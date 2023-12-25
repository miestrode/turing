import sys
from pddlsim.local_simulator import LocalSimulator
from q_learning_agent import *

mode = sys.argv[1]
domain_path = sys.argv[2]
problem_path = sys.argv[3]
policyfile_name = domain_path + "_" + problem_path + "_POLICYFILE"


LocalSimulator().run(domain_path, problem_path, Q_Learning(mode, policyfile_name))
