from pddlsim.executors.executor import Executor
import json
import os.path
from utils import parser
from utils.knowledge_graph import KnowldegeGraph
import random
import utils.file_manager as fm
from learning_manager import LearningManager


class GraphExecuter(Executor):
    """GraphExecuter - execute the best policy to solve problems"""

    def __init__(self):
        self.successor = None

    def initialize(self, services):
        self.services = services

        try:
            self.policy, self.goal_hash = fm.load_policy_file(self.services)
            self.graph = fm.load_knowledge_graph(self.services)
        except IOError:
            # In case we didn't have a chance to learn, learn now till you find your goal
            LearningManager().initialize(self.services, True)
            self.policy, self.goal_hash = fm.load_policy_file(self.services)
            self.graph = fm.load_knowledge_graph(self.services)

    def next_action(self):
        if self.services.goal_tracking.reached_all_goals():
            return None

        state = self.services.perception.get_state()
        self.services.parser.apply_revealable_predicates(state)

        action = self.__get_action(state)

        return action

    def __get_action(self, state):
        state_hash = parser.state_to_hash(state)

        if not (self.policy != None and state_hash in self.policy):
            # We left the right path, recalculating shortest path
            if self.graph.is_contains(state_hash) and self.graph.is_contains(
                self.goal_hash
            ):
                self.policy = self.graph.find_shortest_path(state_hash, self.goal_hash)

        if not (self.policy != None and state_hash in self.policy):
            # We have no info about the current state. Pick random action
            actions = self.services.valid_actions.get()
            return random.choice(actions) if len(actions) > 0 else None

        return self.policy[state_hash]
