from pddlsim.executors.executor import Executor
import os
from utils import parser
from graph_learner import GraphLearner


class LearningManager(Executor):
    """LearningManager manage which learner should we run according to the given domain"""

    def __init__(self):
        self.successor = None

    def initialize(self, services, is_ojt=False):
        self.services = services

        is_determinisitc = parser.is_deterministic_domain(self.services)
        # If the domain is deterministic run the planner, otherwise run the graph executer (that use learning knowledge)
        if is_determinisitc:
            exit(128)

        self.learner = GraphLearner(is_ojt)
        self.learner.initialize(self.services)

    def next_action(self):
        return self.learner.next_action()
