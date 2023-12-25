import json
import abc
import os

from pddlsim.parser_independent import Action


class ActionProbabilitiesUtils(abc.ABCMeta):
    @staticmethod
    def get_initial_probabilities(action):
        if isinstance(action, Action):
            size = 1
        else:
            size = len(action.prob_list)

        return [0] * size

    @staticmethod
    def count_of_action_occurred(action_probabilities):
        return sum(action_probabilities)

    @staticmethod
    def count_of_all_actions_occurred(actions_probabilities):
        return sum(
            [
                ActionProbabilitiesUtils.count_of_action_occurred(action)
                for action in actions_probabilities.values()
            ]
        )

    @staticmethod
    def get_probability(action_probabilities, index):
        count_action_occurred = ActionProbabilitiesUtils.count_of_action_occurred(
            action_probabilities
        )

        if count_action_occurred == 0:
            return 0

        return float(action_probabilities[index]) / count_action_occurred

    @staticmethod
    def get_probabilities(action_probabilities):
        return [
            ActionProbabilitiesUtils.get_probability(action_probabilities, i)
            for i in range(len(action_probabilities))
        ]

    @staticmethod
    def is_deterministic_action(action_probabilities):
        non_zero_effects = 0

        for probability in action_probabilities:
            if probability != 0:
                non_zero_effects += 1

        return non_zero_effects == 1

    @staticmethod
    def is_domain_actually_deterministic(actions_probabilities):
        return any(
            ActionProbabilitiesUtils.is_deterministic_action(action)
            for action in actions_probabilities
        )


class ProbabilitiesLearningHandler:
    def __init__(self, path, actions):
        self.path = path
        self.actions = actions
        self.actions_probabilities = {}

        if os.path.isfile(path):
            self.load_table()
        else:
            self.create_table()

    def create_table(self):
        for action_type, action in self.actions.items():
            self.actions_probabilities[
                action_type
            ] = ActionProbabilitiesUtils.get_initial_probabilities(action)

    def occurred_effect(self, action_type, index):
        self.actions_probabilities[action_type][index] += 1

    def load_table(self):
        with open(self.path, "r") as f:
            self.actions_probabilities = json.load(f)

    def save_table(self):
        with open(self.path, "w") as f:
            json.dump(self.actions_probabilities, f)
