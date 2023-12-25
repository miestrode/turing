import pickle
import random
from os import path
from pddlsim.executors.executor import Executor
from visit_all_executor import VisitAllExecutor


class QTable:
    def __init__(self):
        self.qTable = dict()
        self.stateMap = dict()
        self.prob = dict()
        self.actionMap = {}
        self.known_prob = 10
        self.visited = {}
        self.max_visit = 40

    def get_state_key(self, state):
        key = None
        if state not in self.stateMap.values():
            self.stateMap[len(self.stateMap)] = state
        key = self.stateMap.values().index(state)
        return key

    def get_q_table_s_a(self, state, action):
        state_key = self.get_state_key(state)
        if state_key not in self.qTable.keys():
            self.qTable[state_key] = {}
        if action not in self.qTable[state_key].keys():
            self.qTable[state_key][action] = {"name": action, "value": 0}
        return self.qTable[state_key][action]

    def update_q_table(self, state, action, value):
        state_key = self.get_state_key(state)
        if state_key not in self.qTable.keys():
            self.qTable[state_key] = {}
        if action not in self.qTable[state_key].keys():
            self.qTable[state_key][action] = {"name": action, "value": value}
        self.qTable[state_key][action]["value"] = value

    def get_prob_for_state(self, state, action, new_state):
        state_key = self.get_state_key(state)
        new_state_key = self.get_state_key(new_state)
        if state_key not in self.prob.keys():
            self.prob[state_key] = {}
        if action not in self.prob[state_key].keys():
            self.prob[state_key][action] = {}
        if new_state_key not in self.prob[state_key][action].keys():
            self.prob[state_key][action][new_state_key] = 0
        views = sum([value for value in self.prob[state_key][action].values()])
        self.prob[state_key][action][new_state_key] += 1
        if views > self.known_prob:
            return self.prob[state_key][action][new_state_key] / views
        return None

    def get_max_action_for_state(self, state):
        max_action = -1000
        name = ""
        key = self.get_state_key(state)
        if key not in self.qTable.keys():
            return 0, None
        for action in self.qTable[key].values():
            value = action["value"]
            if value > max_action:
                max_action = action["value"]
                name = action["name"]
        return max_action, name

    def add_to_visited(self, state):
        key = self.get_state_key(state)
        if key not in self.visited.keys():
            self.visited[key] = 0
        self.visited[key] += 1

    def is_max_visited(self):
        return max([vi for vi in self.visited.values()]) > 40


class QLearningExecutionExecutor(Executor):
    def __init__(self, epochs=None):
        super(QLearningExecutionExecutor, self).__init__()
        self.services = None
        #  tables
        self.tables = QTable()
        self.policy_file = ""
        self.visit_all_executor = VisitAllExecutor()

    def initialize(self, services):
        self.services = services
        self.policy_file = (
            "Policy-"
            + self.services.parser.domain_name
            + "-"
            + self.services.parser.problem_name
        )
        if path.exists(self.policy_file):
            self.load_tables(self.policy_file)
        self.visit_all_executor.initialize(self.services)

    def load_tables(self, file_name):
        with open(file_name, "r") as f:
            self.tables = pickle.load(f)

    def next_action(self):
        state = self.services.perception.get_state()
        self.tables.add_to_visited(state)
        if self.services.goal_tracking.reached_all_goals():
            return None
        if self.tables.is_max_visited():
            return self.visit_all_executor.next_action()
        options = self.services.valid_actions.get()
        if len(options) == 0:
            return None
        if len(options) == 1:
            next_action = options[0]
        else:
            next_action = self.choose_from_many(options, state)
        return next_action

    def choose_from_many(self, options, state):
        """
        1. chose if exploration or explotation
        2. chose the next action
        3. return this action
        """
        _, chosen = self.tables.get_max_action_for_state(state)
        if not chosen:
            chosen = random.choice(options)
        return chosen


class QLearningExecutor(Executor):
    def __init__(self, epochs=None):
        super(QLearningExecutor, self).__init__()
        self.services = None
        #  tables
        self.tables = QTable()

        self.policy_file = ""
        # hyperParamaters
        self.lr = 0.01
        self.discount = 0.95
        self.reward = 100
        self.step = -1
        if not epochs:
            epochs = 20
        self.epoch = epochs

        # exploration/explotation paramaters
        self.numOfSteps = 0
        self.explorRate = 1.00
        # prev data
        self.prev_state = None
        self.prev_action = None
        self.already_reward = []

    def initialize(self, services):
        self.services = services
        self.policy_file = (
            "Policy-"
            + self.services.parser.domain_name
            + "-"
            + self.services.parser.problem_name
        )
        if path.exists(self.policy_file):
            self.load_tables(self.policy_file)

    def load_tables(self, file_name):
        with open(file_name, "r") as f:
            self.tables = pickle.load(f)

    def save_tables(self, file_name):
        with open(file_name, "w") as f:
            pickle.dump(self.tables, f)

    def updateQTable(self, prev_state, prev_action, state):
        prob = self.tables.get_prob_for_state(prev_state, prev_action, state)
        if prob is None:
            prob = 1
        q_s_a = self.tables.get_q_table_s_a(prev_state, prev_action)
        q_st_max, _ = self.tables.get_max_action_for_state(state)
        reward = self.get_reward()
        value = (1 - self.lr) * q_s_a["value"] + self.lr * (
            reward + self.discount * q_st_max
        )
        self.tables.update_q_table(prev_state, prev_action, value)

    def finish_run(self):
        self.save_tables(self.policy_file)

    def next_action(self):
        state = self.services.perception.get_state()
        if self.prev_state is not None and self.prev_action is not None:
            self.updateQTable(self.prev_state, self.prev_action, state)
        if self.services.goal_tracking.reached_all_goals():
            self.finish_run()
            return None
        options = self.services.valid_actions.get()
        if len(options) == 0:
            self.finish_run()
            return None
        if len(options) == 1:
            next_action = options[0]
        else:
            next_action = self.choose_from_many(options, state)

        self.prev_state = state
        self.prev_action = next_action

        return next_action

    def choose_from_many(self, options, state):
        """
        1. chose if exploration or explotation
        2. chose the next action
        3. return this action
        """
        chosen = None
        if self.exploration():
            chosen = random.choice(options)
        else:
            _, chosen = self.tables.get_max_action_for_state(state)
            if not chosen:
                chosen = random.choice(options)
        return chosen

    def exploration(self):
        probability = max(self.explorRate, 0.3)
        self.explorRate -= 0.002
        return random.random() < probability

    def get_reward(self):
        goal_parts = []
        for goal in self.services.parser.goals:
            goal_parts += goal.parts
        goal_reward = 0
        for part in goal_parts:
            if (
                self.services.parser.test_condition(
                    part, self.services.perception.get_state()
                )
                and part not in self.already_reward
            ):
                self.already_reward += [part]
                goal_reward += 1
        return goal_reward * self.reward + self.step
