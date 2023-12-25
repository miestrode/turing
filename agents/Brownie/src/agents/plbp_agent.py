import random

from pddlsim import planner
from pddlsim.executors.executor import Executor
from pddlsim.fd_parser import FDParser
from pddlsim.parser_independent import PDDL, Action, Literal, Not, StripsStringVisitor

from src.editors.domain_editor import DomainEditor
from src.handlers.probabilities_learning_handler import ActionProbabilitiesUtils


class PLBPAgnet(Executor):
    def __init__(self, probabilities_learning_handler, reveal_learning_handler, mode):
        super(PLBPAgnet, self).__init__()
        self.mode = mode
        self.expected_state = None
        self.steps = []
        self.custom_parser = None
        self.search_state = None
        self.prev_action_type = None
        self.deterministic_parser = None
        self.reveal_goals = []
        self.prev_action = None
        self.prev_state = None
        self.prev_reveal_state = None
        self.probabilities_learning_handler = probabilities_learning_handler
        self.reveal_learning_handler = reveal_learning_handler

    def get_deterministic_parser(self):
        domain_path = DomainEditor.get_deterministic_domain_path(
            self.services.parser.domain_name
        )
        custom_parser = FDParser(domain_path, self.services.pddl.problem_path)
        return custom_parser

    def initialize(self, services):
        self.services = services
        self.custom_parser = self.get_custom_parser()
        self.prev_reveal_state = self.get_state()
        self.deterministic_parser = self.get_deterministic_parser()
        self.search_state = self.services.parser.copy_state(self.get_state())
        self.steps = self.plan()

    def get_state(self):
        return self.services.perception.state

    def get_custom_parser(self):
        domain_path = DomainEditor.get_deterministic_domain_path(
            self.services.parser.domain_name
        )
        custom_parser = FDParser(domain_path, self.services.pddl.problem_path)
        return custom_parser

    @staticmethod
    def action_string(action_name, params):
        params = " ".join([var for var in params])
        return "(" + action_name + " " + params + ")"

    def get_expected_state(self, action):
        if action == "current_state":
            return self.prev_state

        new_copy_state = self.services.parser.copy_state(self.prev_state)
        self.deterministic_parser.apply_action_to_state(
            action, new_copy_state, check_preconditions=False
        )

        return new_copy_state

    def get_all_expected_states_options(self, action_sig):
        action_name, param_names = PDDL.parse_action(action_sig)
        action = self.services.parser.actions[action_name]

        custom_actions = []

        if isinstance(action, Action):
            custom_actions.append(
                self.action_string(
                    DomainEditor.get_action_name_of_probabilistic_action(action, 0),
                    param_names,
                )
            )
        else:
            for i in range(len(action.prob_list)):
                if len(action.addlists[i]) > 0 or len(action.dellists[i]) > 0:
                    custom_actions.append(
                        self.action_string(
                            DomainEditor.get_action_name_of_probabilistic_action(
                                action, i
                            ),
                            param_names,
                        )
                    )
                else:
                    custom_actions.append("current_state")

        expected_states = [self.get_expected_state(action) for action in custom_actions]

        return expected_states

    @staticmethod
    def get_diff_between_states(state, other_state):
        add_diff = {}
        del_diff = {}

        for action_name, values in state.items():
            add_diff[action_name] = values - other_state[action_name]
            del_diff[action_name] = other_state[action_name] - values

        return add_diff, del_diff

    def store_reveals(self, diff):
        strip_string_visitor = StripsStringVisitor()

        literals = [
            Literal(key, list(value)[0]).accept(strip_string_visitor)
            for key, value in diff[0].items()
            if len(list(value))
        ]
        not_literals = [
            Not(Literal(key, list(value)[0])).accept(strip_string_visitor)
            for key, value in diff[1].items()
            if len(list(value))
        ]

        self.reveal_learning_handler.append(literals)
        self.steps = self.plan()

    def get_picked_index_effect_and_store_reveal(self, action_sig):
        optional_states = self.get_all_expected_states_options(action_sig)
        current_state = self.get_state()

        min_diff = None
        index = None
        min_diff_lists = []

        for i in range(len(optional_states)):
            add_diff, del_diff = self.get_diff_between_states(
                current_state, optional_states[i]
            )

            diff = sum(
                [len(list(temp)) for temp in add_diff.values()]
                + [len(list(temp)) for temp in del_diff.values()]
            )

            if min_diff is None or diff < min_diff:
                index = i
                min_diff = diff
                min_diff_lists = [add_diff, del_diff]

        if sum([len(list(temp)) for temp in min_diff_lists[0].values()]) > 0:
            reveals = min_diff_lists
            self.store_reveals(reveals)
        return index

    def update_probabilities_table(self, action, index):
        action_name = PDDL.parse_action(action)[0]
        self.probabilities_learning_handler.occurred_effect(action_name, index)

    def get_state_with_reveal(self):
        state = self.services.parser.copy_state(self.get_state())

        reveals = self.reveal_learning_handler.reveals

        for reveal in reveals:
            action_name, parameters = PDDL.parse_action(reveal)
            state[action_name].add(tuple(parameters))

        return state

    def build_current_state_problem_file(self):
        if len(self.services.goal_tracking.uncompleted_goals) > 0:
            self.services.parser.generate_problem(
                "customed_problem",
                self.get_state_with_reveal(),
                self.services.goal_tracking.uncompleted_goals[0],
            )

    @staticmethod
    def is_states_equals(state_a, state_b):
        return state_a == state_b

    def store_expected_state(self, custom_deterministic_action):
        state = self.get_state()

        new_copy_state = self.services.parser.copy_state(state)
        self.custom_parser.apply_action_to_state(
            custom_deterministic_action, new_copy_state, check_preconditions=False
        )

        self.expected_state = new_copy_state

    def plan(self):
        self.build_current_state_problem_file()
        return planner.make_plan(self.custom_parser.domain_path, "customed_problem")

    def pick_goal(self):
        return self.services.goal_tracking

    def save_tables(self):
        self.probabilities_learning_handler.save_table()
        self.reveal_learning_handler.save_reveal_file()

    def save_and_exit(self):
        self.save_tables()
        exit(128)

    def next_action(self):
        if self.prev_state is not None:
            index = self.get_picked_index_effect_and_store_reveal(self.prev_action)
            self.update_probabilities_table(self.prev_action, index)

        action = None

        if self.services.goal_tracking.reached_all_goals():
            if self.mode == "-L":
                self.save_and_exit()
            return None
        valid_actions = self.services.valid_actions.get()
        if len(valid_actions) == 0:
            return None

        if (
            ActionProbabilitiesUtils.count_of_all_actions_occurred(
                self.probabilities_learning_handler.actions_probabilities
            )
            % 100
            == 99
        ):
            self.save_tables()

            # DomainEditor.write_filtered_effects_deterministic_domain_from_stochastic_domain(
            #    self.services.parser, self.probabilities_learning_handler.actions_probabilities, 0.15)

        if len(valid_actions) == 1:
            action = valid_actions[0]

        elif (
            ActionProbabilitiesUtils.count_of_all_actions_occurred(
                self.probabilities_learning_handler.actions_probabilities
            )
            < 100
        ):
            action = self.__pick_next_action_train_probabilities(valid_actions)

        elif len(self.steps) > 0:
            if self.mode == "-L":
                self.save_and_exit()

            if self.expected_state and not self.is_states_equals(
                self.get_state(), self.expected_state
            ):
                self.steps = self.plan()
            if len(self.steps) > 0:
                custom_action = self.steps.pop(0).lower()

                self.store_expected_state(custom_action)

                custom_action_name, action_parameters = custom_action.split(" ", 1)
                action_name = DomainEditor.get_action_name_from_custom_action(
                    custom_action_name
                )

                action = " ".join([action_name, action_parameters])

        if not action:
            action = self.__pick_next_action(valid_actions)

        self.prev_action = action
        self.prev_action_type = PDDL.parse_action(action)[0]
        self.prev_state = self.get_state()

        return action

    @staticmethod
    def get_predicates_in_state(state):
        return sum([len(list(value)) for key, value in state.items() if key != "="])

    def __pick_next_action(self, valid_actions):
        copy_state = self.services.parser.copy_state(self.search_state)
        temp2 = self.get_predicates_in_state(self.search_state)

        min_size = min(len(valid_actions), 100)
        actions = random.sample(valid_actions, min_size)

        for action in actions:
            self.services.parser.apply_action_to_state(
                action, copy_state, check_preconditions=False
            )

            if self.get_predicates_in_state(copy_state) > temp2:
                self.search_state = copy_state
                return action

        return self.__pick_next_action_train_probabilities(actions)

    def __pick_next_action_train_probabilities(self, valid_actions):
        min_count_action_occurred = None
        action = None

        for optional_action in valid_actions:
            action_type = PDDL.parse_action(optional_action)[0]

            count_action_occurred = ActionProbabilitiesUtils.count_of_action_occurred(
                self.probabilities_learning_handler.actions_probabilities[action_type]
            )

            if (
                min_count_action_occurred is None
                or count_action_occurred < min_count_action_occurred
            ):
                min_count_action_occurred = count_action_occurred
                action = optional_action

        return action
