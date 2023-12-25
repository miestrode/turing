import pickle
import random
from os import path

from pddlsim.executors.executor import Executor
from state_list import StateList


class VisitAllExecutor(Executor):
    def __init__(self):
        super(VisitAllExecutor, self).__init__()
        self.services = None
        #  tables
        self.executor = None
        self.prev_state = None
        self.prev_action = None
        self.model = StateList()
        self.model_file = ""

    # initialize the executor
    def initialize(self, services):
        self.services = services
        self.model_file = (
            self.services.parser.domain_name
            + "-"
            + self.services.parser.problem_name.split("-")[0]
        )
        if path.exists(self.model_file):
            self.load_tables(self.model_file)

    def next_action(self):
        state = self.services.perception.get_state()
        if self.prev_action and self.prev_state:
            self.model.add_to_map(self.prev_state, self.prev_action, state)
        self.model.add_to_visited(state)
        if self.services.goal_tracking.reached_all_goals():
            return None
        options = self.services.valid_actions.get()
        if len(options) == 0:
            return None
        if len(options) == 1:
            next_action = options[0]
        else:
            next_action = self.choose_from_many(options, state)
        self.prev_action = next_action
        self.prev_state = state
        return next_action

    def choose_from_many(self, options, state):
        chosen = self.choose_lower_visited_action(state, options)
        if not chosen:
            chosen = random.choice(options)
        return chosen

    def choose_lower_visited_action(self, state, options):
        min = 15000
        next_action = None
        for op in options:
            value = self.model.get_state_visited_by_action(state, op)
            if value < min:
                min = value
                next_action = op
        return next_action

    def load_tables(self, file_name):
        with open(file_name, "r") as f:
            self.model = pickle.load(f)

    def save_tables(self, file_name):
        with open(file_name, "w") as f:
            pickle.dump(self.model, f)
