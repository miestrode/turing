import sys
import random
import json
import hashlib
from os import path
from pddlsim.executors.executor import Executor
from pddlsim.parser_independent import Literal
from pddlsim.local_simulator import LocalSimulator
import pddlsim.planner as planner


# Q-learning executor
class QLearningExecutor(Executor):
    """
    QLearningExecutor - executes a step based on the Q-learning algorithm.
    """

    # Constructor
    def __init__(self, domain_file, problem_file):
        super(QLearningExecutor, self).__init__()
        self.domain_file_name = domain_file
        self.problem_file_name = problem_file

    # Initialization
    def initialize(self, services):
        self.services = services
        self.epsilon = 0.2
        self.lr = 0.1
        self.gamma = 0.95
        self.n = 0
        self.use_dyna_q = False
        self.domain_path = self.services.pddl.domain_path
        self.problem_path = self.services.pddl.problem_path
        self.policy_file = self.problem_file_name.replace(".pddl", "_policy")
        self.environment = self.problem_file_name.split("/")[-1].split("-")[0].replace(".pddl", "")
        self.check_if_deterministic()
        self.q_table = {}
        self.full_current_state = self.services.perception.get_state()
        self.current_state = None
        self.previous_state = None
        self.previous_action = None
        self.reward = None
        self.reached_all_goals = False
        self.total_sub_goals = self.get_num_uncompleted_sub_goals()
        self.uncompleted_sub_goals = self.total_sub_goals
        self.prev_uncompleted_sub_goals = self.total_sub_goals
        self.dead_end = False
        if self.use_dyna_q:
            self.model_file = self.problem_file_name.replace(".pddl", "_model")
            self.model = {}

    def check_if_deterministic(self):
        try:
            planner_steps = planner.make_plan(self.domain_file_name, self.problem_file_name)
            if len(planner_steps) <= 0:
                return
        except:
            return
        exit(128)

    # Return the next action to apply
    def next_action(self):
        first_step = False
        first_learn_iter = False
        # Get current state
        self.full_current_state = self.services.perception.get_state()
        self.current_state = self.get_hash_state(self.full_current_state)
        # Get the actions that can be applied
        valid_actions = self.services.valid_actions.get()

        # Test if all goals have been reached
        if self.services.goal_tracking.reached_all_goals():
            self.reached_all_goals = True
            if self.current_state not in self.q_table:
                # Add the current state and the next valid actions to the q-table with q-value 0
                self.initialize_next_actions(valid_actions)
            # Reward for reaching the goal
            self.reward = self.get_reward()
            self.update_q_table_from_learning()
            if self.use_dyna_q:
                self.update_model()
                self.update_q_table_from_model()

            try:
                # Run the executor again
                print LocalSimulator().run(self.domain_file_name, self.problem_file_name,
                                           QLearningExecutor(self.domain_file_name, self.problem_file_name))
            except:
                # Finish learning phase
                sys.exit(0)

        # If this is the first step in this learning iteration
        if self.previous_state is None:
            first_step = True
            # If this is the first learning iteration
            if not path.exists(self.policy_file):
                first_learn_iter = True
            # If this is not the first learning iteration
            else:
                # Load q-table from the policy file
                self.load_q_table_from_file()
                if self.use_dyna_q:
                    # Load model from the model file
                    self.load_model_from_file()

        # If a dead end has been reached
        if len(valid_actions) == 0:
            if not first_step:
                self.dead_end = True
                # Reward for moving to dead end
                self.reward = self.get_reward()
                self.update_q_table_from_learning()
                if self.use_dyna_q:
                    self.update_model()
                    self.update_q_table_from_model()
            return None

        # If this is the first time at the current state
        if self.current_state not in self.q_table:
            # Add the current state and the next valid actions to the q-table with q-value 0
            self.initialize_next_actions(valid_actions)

        if first_step and first_learn_iter:
            # Choose a random valid action
            action = random.choice(valid_actions)
        else:
            # Choose an action using the epsilon greedy algorithm
            action = self.choose_epsilon_greedy(valid_actions)
        if not first_step:
            # Reward for a regular move action
            self.reward = self.get_reward()
            self.update_q_table_from_learning()
            if self.use_dyna_q:
                self.update_model()
                self.update_q_table_from_model()

        self.previous_state = self.current_state
        self.previous_action = action
        return action

    def get_num_uncompleted_sub_goals(self):
        if self.reached_all_goals:
            return 0
        try:
            sub_goals = 0
            # Get all sub-goals
            for sub_goal in self.services.goal_tracking.uncompleted_goals[0].parts:
                # If sub-goal is a literal
                if type(sub_goal) == Literal:
                    if not sub_goal.test(self.full_current_state):
                        sub_goals += 1
                else:
                    for part in sub_goal.parts:
                        if not part.test(self.full_current_state):
                            sub_goals += 1
            return sub_goals
        except:
            return 0

    def get_reward(self):
        if self.dead_end:
            return -100
        if self.reached_all_goals:
            return 100
        self.uncompleted_sub_goals = self.get_num_uncompleted_sub_goals()
        achieved_sub_goals = self.prev_uncompleted_sub_goals - self.uncompleted_sub_goals
        completed_sub_goals = self.total_sub_goals - self.uncompleted_sub_goals
        reward = 0
        # Achieving sub-goals
        if achieved_sub_goals > 0:
            for i in range(achieved_sub_goals):
                reward += 50 * ((completed_sub_goals - i) / self.total_sub_goals)
        # Losing of sub-goals
        elif achieved_sub_goals < 0:
            for i in range(-achieved_sub_goals):
                reward -= 50 * ((completed_sub_goals + (i+1)) / self.total_sub_goals) + 1
        else:
            reward = -1
        self.prev_uncompleted_sub_goals = self.uncompleted_sub_goals
        return reward

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

    def choose_epsilon_greedy(self, valid_actions):
        # Get a random number between 0 and 1
        p = random.random()
        # If the random number is less than epsilon
        if p < self.epsilon:
            # Exploration (choose a random valid action)
            action = self.exploration(valid_actions)
        else:
            # Exploitation (choose the action with the highest q-value for this state from the q-table)
            action = self.choose_using_policy()
        return action

    # Exploration
    def exploration(self, valid_actions):
        # Choose a random valid action
        random_action = random.choice(valid_actions)
        return random_action

    # Exploitation
    def choose_using_policy(self):
        # Choose the action with the max value
        max_value = None
        max_actions = []
        actions = self.q_table[self.current_state]
        for action in actions:
            if max_value is None:
                max_value = actions[action]
                max_actions.append(action)
            elif actions[action] == max_value:
                max_actions.append(action)
            elif actions[action] > max_value:
                max_value = actions[action]
                max_actions = [action]
        if len(max_actions) <= 1:
            max_action = max_actions.pop(0)
        else:
            max_action = random.choice(max_actions)
        return max_action

    def get_max_q_value(self, state):
        # Get the max value of all action can be apply from this state
        max_value = None
        actions = self.q_table[state]
        for action in actions:
            if max_value is None:
                max_value = actions[action]
            elif actions[action] > max_value:
                max_value = actions[action]
        return max_value

    def update_q_table_from_learning(self):
        # Calculate the new q-value
        if self.dead_end:
            max_next_q_value = -100
        else:
            max_next_q_value = self.get_max_q_value(self.current_state)
        old_q_value = self.q_table[self.previous_state][self.previous_action]
        new_q_value = old_q_value + self.lr * (self.reward + self.gamma * max_next_q_value - old_q_value)
        self.q_table[self.previous_state][self.previous_action] = new_q_value
        # Save q-table to the policy file
        self.save_q_table_to_file()

    def initialize_next_actions(self, valid_actions):
        self.q_table[self.current_state] = {}
        for action in valid_actions:
            self.q_table[self.current_state][action] = 0
        # Save q-table to the policy file
        self.save_q_table_to_file()

    def save_q_table_to_file(self):
        # Open the policy file to save the q-table
        policy_file = open(self.policy_file, "w")
        # Convert q_table into JSON and write it to the file
        policy_file.write(json.dumps(self.q_table))
        policy_file.close()

    def load_q_table_from_file(self):
        if path.getsize(self.policy_file) > 0:
            # Open the policy file to load the q-table
            policy_file = open(self.policy_file, "r")
            # Convert q_table from JSON to Python
            self.q_table = json.load(policy_file)
            policy_file.close()
        else:
            self.q_table = {}

    def update_q_table_from_model(self):
        for i in range(self.n):
            # Choose random previously observed state
            state = random.choice(list(self.model.keys()))
            # Choose random action previously taken in this state
            action = random.choice(list(self.model[state].keys()))
            # Calculate the weighted amount of reward and max q-value using the probabilities
            total_visits = 0
            weighted_reward = 0
            weighted_max_q = 0
            # Calculate number of visits in this state
            for new_state, info in self.model[state][action].items():
                total_visits += info[1]
            for new_state, info in self.model[state][action].items():
                probability = info[1] / total_visits
                weighted_reward += probability * info[0]
                weighted_max_q = self.get_max_q_value(new_state)
            # Update Q-table
            old_q_value = self.q_table[state][action]
            new_q_value = old_q_value + self.lr * (weighted_reward + self.gamma * weighted_max_q - old_q_value)
            self.q_table[state][action] = new_q_value
            # Save q-table to the policy file
            self.save_q_table_to_file()

    def update_model(self):
        if self.previous_state not in self.model:
            self.model[self.previous_state] = {}
        if self.previous_action not in self.model[self.previous_state]:
            self.model[self.previous_state][self.previous_action] = {}
        if self.current_state not in self.model[self.previous_state][self.previous_action]:
            self.model[self.previous_state][self.previous_action][self.current_state] = [self.reward, 1]
        else:
            self.model[self.previous_state][self.previous_action][self.current_state][1] += 1
        # Save the model to the model file
        self.save_model_to_file()

    def save_model_to_file(self):
        # Open the model file to save the model
        model_file = open(self.model_file, "w")
        # Convert the model into JSON and write it to the file
        model_file.write(json.dumps(self.model))
        model_file.close()

    def load_model_from_file(self):
        # Open the model file to load the model
        model_file = open(self.model_file, "r")
        # Convert the model from JSON to Python
        self.model = json.load(model_file)
        model_file.close()
