import sys
from os import path
import random
import json
import hashlib
from pddlsim.local_simulator import LocalSimulator
from pddlsim.executors.executor import Executor
from q_learning_executor import QLearningExecutor
from converter import Converter
import pddlsim.planner as planner


# Learned policy executor
class MyExecutor(Executor):
    """
    MyExecutor - executes a step based on the policy learned in the learning phase.
    """

    # Constructor
    def __init__(self, domain_file, problem_file):
        super(MyExecutor, self).__init__()
        self.domain_file_name = domain_file
        self.problem_file_name = problem_file
        self.policy_file = problem_file.replace(".pddl", "_policy")

    # Initialization
    def initialize(self, services):
        self.services = services
        self.domain_path = self.services.pddl.domain_path
        self.problem_path = self.services.pddl.problem_path
        self.init_problem_content = None
        self.init_predicates_str = None
        self.new_domain_path = None
        self.is_deterministic = False
        self.converted_to_deterministic = False
        self.hidden_objects = False
        self.planner_steps = []
        self.current_state = None
        self.previous_state = None
        self.previous_action = None
        self.q_table = []
        self.last_actions = []

        self.is_policy_exists = (
            path.exists(self.policy_file) and path.getsize(self.policy_file) > 0
        )
        if self.is_policy_exists:
            self.q_table = self.load_q_table_from_file()
        else:
            self.is_deterministic = self.check_if_deterministic()
            if not self.is_deterministic:
                converter = Converter(self.domain_path)
                converter.convert_to_deterministic_high_prob()
                self.converted_to_deterministic = True
                self.new_domain_path = converter.new_domain_path

    # Return the next action to apply
    def next_action(self):
        # Test if all goals have been reached
        if self.services.goal_tracking.reached_all_goals():
            # None is used to indicate that all goals have been reached
            return None

        # Deterministic domain
        if self.is_deterministic:
            action = self.deterministic_next_action()
            return action

        # Get current state
        full_current_state = self.services.perception.get_state()
        self.current_state = self.get_hash_state(full_current_state)
        # Get the actions that can be applied
        valid_actions = self.services.valid_actions.get()
        if len(valid_actions) == 0:
            return None

        # Converted-to-deterministic domain
        if self.converted_to_deterministic and not self.hidden_objects:
            action = self.new_deterministic_next_action(
                full_current_state, valid_actions
            )
            return action

        # Non-deterministic domain with policy file
        if self.is_policy_exists:
            action = self.policy_next_action(valid_actions)
            return action

        # Choose a random valid action from the non recently selected actions
        action = self.get_non_recently_random_action(valid_actions)
        return action

    def check_if_deterministic(self):
        try:
            self.planner_steps = self.get_plan(
                self.domain_file_name, self.problem_file_name
            )
            if len(self.planner_steps) > 0:
                return True
            else:
                return False
        except:
            return False

    def get_plan(self, domain_file, problem_file):
        steps = planner.make_plan(domain_file, problem_file)
        return steps

    # Choose a random valid action from the non recently selected actions
    def get_non_recently_random_action(self, valid_actions):
        new_valid_actions = list(valid_actions)
        for act in self.last_actions:
            try:
                new_valid_actions.remove(act)
            except:
                pass
        if (
            self.previous_state is not None
            and self.current_state == self.previous_state
        ):
            new_valid_actions.append(self.last_actions[0])
        if len(new_valid_actions) > 0:
            action = random.choice(new_valid_actions)
        else:
            action = random.choice(valid_actions)
        # Add the chosen action to the last actions list
        if len(self.last_actions) >= 5:
            self.last_actions.pop(0)
        self.last_actions.append(action)
        return action

    def deterministic_next_action(self):
        if len(self.planner_steps) > 0:
            return self.planner_steps.pop(0).lower()
        return None

    def new_deterministic_next_action(self, full_current_state, valid_actions):
        if self.init_problem_content is None:
            self.get_init_predicates_string()
        if self.current_state == self.previous_state:
            return self.previous_action
        current_predicates_str = self.get_predicates_string(full_current_state)
        new_problem_content = self.init_problem_content.replace(
            self.init_predicates_str, current_predicates_str
        )
        new_problem_path = "new_problem.pddl"
        with open(new_problem_path, "w") as new_problem:
            new_problem.write(new_problem_content)
        try:
            self.planner_steps = self.get_plan(self.new_domain_path, new_problem_path)
        except:
            self.hidden_objects = True
            # Choose a random valid action
            random_action = random.choice(valid_actions)
            return random_action
        # Get the next action in the new deterministic domain
        deterministic_action = self.deterministic_next_action()
        # Convert to non-deterministic action
        det_action_name = deterministic_action.split()[0]
        non_det_action_name = det_action_name.rsplit("_", 1)[0]
        non_deterministic_action = deterministic_action.replace(
            det_action_name, non_det_action_name
        )
        self.previous_state = self.current_state
        self.previous_action = non_deterministic_action
        return non_deterministic_action

    def get_predicates_string(self, state):
        predicates = self.services.parser.predicates_from_state(state)
        pred_str = "(:init\n"
        for pred in predicates:
            pred_str += "\t" + pred + "\n"
        pred_str += ")\n"
        return pred_str

    def get_init_predicates_string(self):
        with open(self.problem_path, "r") as problem_file:
            self.init_problem_content = problem_file.read()
        in_init = False
        init_pred_str = ""
        open_parenthesis = 0
        close_parenthesis = 0
        for line in self.init_problem_content.splitlines():
            if "init" in line:
                in_init = True
            if in_init:
                open_parenthesis += line.count("(")
                close_parenthesis += line.count(")")
                init_pred_str += line + "\n"
                if 0 < open_parenthesis <= close_parenthesis:
                    break
        self.init_predicates_str = init_pred_str

    def policy_next_action(self, valid_actions):
        # Choose the action with the highest q-value for this state from the q-table
        action = self.choose_using_policy(valid_actions)
        if len(self.last_actions) >= 10:
            self.last_actions.pop(0)
        self.last_actions.append(action)
        return action

    def choose_using_policy(self, valid_actions):
        actions = self.q_table[self.current_state]
        # If the actions that can be apply from this state are not in the q-table
        if len(actions) == 0:
            # Choose a random valid action
            random_action = random.choice(valid_actions)
            return random_action
        if len(self.last_actions) >= 10 and len(set(self.last_actions)) <= 2:
            # Choose a random valid action
            random_action = random.choice(valid_actions)
            return random_action
        # Choose the action with the max value
        max_value = None
        max_action = None
        for action in actions:
            if max_value is None:
                max_value = actions[action]
                max_action = action
            elif actions[action] > max_value:
                max_value = actions[action]
                max_action = action
        return max_action

    def load_q_table_from_file(self):
        # Open the policy file to load the q-table
        policy_file = open(self.policy_file, "r")
        # Convert q_table from JSON to Python
        q_table = json.load(policy_file)
        policy_file.close()
        return q_table

    def get_hash_state(self, state):
        for key, value in state.items():
            if isinstance(value, set):
                # Convert the set into a sorted list
                state[key] = list(value)
                state[key].sort()
        # Convert the state dictionary into JSON string
        json_state = json.dumps(state, sort_keys=True)
        hash_state = hashlib.sha1(json_state).hexdigest()
        return hash_state


# Read command line arguments
input_flag = sys.argv[1]
domain_path = sys.argv[2]
problem_path = sys.argv[3]

# Run the correct agent according to the input flag
if input_flag == "-L":  # Learning phase
    print(
        LocalSimulator().run(
            domain_path, problem_path, QLearningExecutor(domain_path, problem_path)
        )
    )
elif input_flag == "-E":  # Execution phase
    print(
        LocalSimulator().run(
            domain_path, problem_path, MyExecutor(domain_path, problem_path)
        )
    )
else:
    raise NameError("Invalid input flag")
