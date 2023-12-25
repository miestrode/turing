import time
import pickle
import sys
from os import path

import pddlsim.parser_independent
from pddlsim.local_simulator import LocalSimulator
from pddlsim.executors.executor import Executor
from state_list import StateList

from plan_dispatcher import PlanDispatcher
from q_learning_executor import QLearningExecutor, QLearningExecutionExecutor
from visit_all_executor import VisitAllExecutor



class LearningExecutor(Executor):
    def __init__(self):
        super(LearningExecutor, self).__init__()
        self.services = None
        #  tables
        self.executor = None
        self.prev_state = None
        self.prev_action = None
        self.model = StateList()
        self.model_file = ""
        self.time = time.time()

    # initialize the executor
    def initialize(self, services):
        self.services = services
        self.model_file = self.services.parser.domain_name + "-" + self.services.parser.problem_name.split('-')[0]
        if path.exists(self.model_file):
            self.load_tables(self.model_file)
        hidden = False
        probs = False
        failure = False
        if len(self.services.parser.revealable_predicates) > 0:
            hidden = True
        if sum([1 for act in self.services.parser.actions.values() if type(act) == pddlsim.parser_independent.ProbabilisticAction]) >0:
            probs = True
        if len(self.services.parser.failure_conditions) > 0:
            failure = True
        if not hidden and not probs and not failure:
            self.executor = PlanDispatcher()
        else :
            self.executor = QLearningExecutor()
        self.executor.initialize(self.services)

    def next_action(self):
        if time.time() - self.time > 40:
            self.save_tables(self.model_file)
            self.time = time.time()
        state = self.services.perception.get_state()
        if self.prev_action and self.prev_state:
            self.model.add_to_map(self.prev_state,self.prev_action,state)
        action = self.executor.next_action()
        if action:
            self.prev_action = action
            self.prev_state = state
            return action
        self.finish_run()

    def load_tables(self, file_name):

        with open(file_name, 'r') as f:
            self.model = pickle.load(f)

    def save_tables(self, file_name):
        with open(file_name, 'w') as f:
            pickle.dump(self.model, f)

    def finish_run(self):
        self.save_tables(self.model_file)


class ExecutionExecutor(Executor):
    def __init__(self):
        super(ExecutionExecutor, self).__init__()
        self.services = None
        #  tables
        self.executor = None

    def initialize(self, services):
        self.services = services

        hidden = False
        probs = False
        failure = False
        if len(self.services.parser.revealable_predicates) > 0:
            hidden = True
        if sum([1 for act in self.services.parser.actions.values() if
                type(act) == pddlsim.parser_independent.ProbabilisticAction]) > 0:
            probs = True
        if len(self.services.parser.failure_conditions) > 0:
            failure = True

        if not hidden and not probs and not failure:
            self.executor = PlanDispatcher()
        else:
            self.policy_file = "Policy-" + self.services.parser.domain_name + "-" + self.services.parser.problem_name
            if path.exists(self.policy_file):
                self.executor = QLearningExecutionExecutor()
            else:
                self.executor = VisitAllExecutor()
        self.executor.initialize(self.services)

    def next_action(self):
        return self.executor.next_action()


input_flag = sys.argv[1]
domain_path = sys.argv[2]
problem_path = sys.argv[3]

if input_flag == '-L': # learning
    for i in range(200):
        print LocalSimulator().run(domain_path, problem_path,LearningExecutor())
elif input_flag == '-E':  # execution
    print LocalSimulator().run(domain_path, problem_path, ExecutionExecutor())
else:
    raise NameError('Wrong input flag, options:  "-L" for learning or "-E" for execution')
