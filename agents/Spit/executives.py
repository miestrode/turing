from __future__ import division
import os
import signal

import pddlsim
import json
import random
import pddlsim.planner as planner
from pddlsim.executors.executor import Executor
import hashlib
import collections
import numpy as np

#####################################################################
# this is a base class, the other executors below inherit it.
#####################################################################
class BaseExecutor(object):

    def represent_state(self, state):
        new_dict = collections.OrderedDict(sorted(state.items()))
        for key in state:
            new_dict[key] = sorted(list(state[key]))
        state_json = json.dumps(new_dict)
        return hashlib.sha224(state_json).hexdigest()

    def load_table(self):
        with open(self.policy_file, "r") as file:
            self.Qtable = json.load(file)
            file.close()

    def max_action(self, state, actions):
        best = actions[0]
        if state not in self.Qtable.keys():
            return random.choice(actions)
        for action in actions:
            if self.Qtable[state][action] > self.Qtable[state][best]:
                best = action
        return best

    def is_deterministic(self, actions):
        for action in actions.values():
            if hasattr(action, 'prob_list'):
                for prob in action.prob_list:
                    if prob < 1:
                        return False
        return True

#######################################################################
## this executive runs when -L flag in given.
## updates the policy file by Q-learning algorithm
#######################################################################
class Q_Learner(BaseExecutor):

    def __init__(self, process_num, queue, t, func):
        self.process_id = process_num
        self.learn_rate = 0.5
        self.discount = 0.9
        self.Qtable = {}
        self.count = {}
        self.reset_past()
        self.current_score = 0
        self.goal = None
        self.simulator = None
        self.goal_intersections = 0
        self.raw_initial_state = None
        self.policy_file = None
        self.temp_t = t
        self.t_func = func
        self.T = self.t_func(self.temp_t)
        self.queue = queue
        self.initial_t = t
        self.t_is_1_count = 0

    def initialize(self, services, sim):
        self.services = services
        self.policy_file = self.services.parser.domain_name + "_" + \
                           self.services.parser.problem_name + "_" + self.process_id.__str__()
        if self.is_deterministic(self.services.parser.actions):
            exit(128)
        if os.path.isfile("./" + self.policy_file):
            self.load_table()

        self.goal = self.services.parser.goals[0]
        self.goal_intersections = self.count_goals_intersections(self.goal)
        self.raw_initial_state = services.parser.initial_state
        self.simulator = sim
        signal.signal(signal.SIGTERM, self.save_table)
        signal.signal(signal.SIGINT, self.save_table)

    def next_action(self):
        current_state = self.services.perception.get_state()
        actions = self.services.valid_actions.get()
        state_hash = self.represent_state(current_state)
        self.add_to_tables(actions, state_hash)
        r = self.reward(state_hash)

        self.services.goal_tracking.dirty = True
        if self.services.goal_tracking.reached_all_goals():
            self.update_table(state_hash, r)
            # return agent to starting state
            self.simulator.set_state(self.raw_initial_state)
            self.services.perception.dirty = True
            current_state = self.services.perception.get_state()
            actions = self.services.valid_actions.get()
            state_hash = self.represent_state(current_state)
            self.add_to_tables(actions, state_hash)
            # delete memory:
            self.reset_past()
            self.services.goal_tracking.uncompleted_goals = self.services.parser.goals[:]
            r = self.reward(state_hash)

        if self.last_action is not None:
            self.update_table(state_hash, r)

        actions_distribution = self.get_actions_prob(state_hash)
        action = np.random.choice(sorted(actions), p=actions_distribution)

        self.last_action = action
        if self.last_state != state_hash:
            self.last_state = state_hash
        #save last five states:
        if state_hash not in self.past_few_states:
            self.past_few_states.append(state_hash)
        ## scheduals:
        self.temp_t -= 1
        self.T = self.t_func(self.temp_t)
        if self.T == 1:
            self.t_is_1_count += 1
        if self.t_is_1_count > 3:
            self.initial_t = 0.99*self.initial_t
            self.temp_t = self.initial_t
            self.t_is_1_count = 0
        self.count[state_hash][action] += 1
        return action

    def update_table(self, state_hash, r):
        self.Qtable[self.last_state][self.last_action] = self.learn_rate * \
                (r + self.discount * sum(self.get_actions_prob(state_hash))) + \
                 (1 - self.learn_rate) * self.Qtable[self.last_state][self.last_action]

    def add_to_tables(self, actions, state):
        if state not in self.Qtable.keys():
            self.Qtable[state] = {}
        if state not in self.count.keys():
            self.count[state] = {}
        for action in actions:
            if action not in self.Qtable[state]:
                self.Qtable[state][action] = 0
            if action not in self.count[state]:
                self.count[state][action] = 0

    def reward(self, state):
        if state == self.last_state:
            return -3
        if state in self.past_few_states:
            return -20
        new_score = self.get_goals_score(self.goal)
        if new_score > self.current_score:
            self.current_score = new_score
            r = new_score / self.goal_intersections * 50
            return r
        if new_score < self.current_score:
            self.current_score = new_score
            return -12
        return -1


    def save_table(self, signum, frame):
        self.Qtable["name"] = self.policy_file
        with open(self.policy_file, 'w') as outfile:
            json.dump(self.Qtable, outfile)
        outfile.close()
        self.queue.put(json.dumps(self.Qtable))
        print "process finished" + self.process_id.__str__()
        exit(signum)

    def get_goals_score(self, goal):
        score = 0
        if self.services.parser.test_condition(goal, self.services.perception.get_state()):
            score = 1
        if isinstance(goal, pddlsim.parser_independent.Literal):
            return score
        return sum([self.get_goals_score(part) for part in goal.parts]) / len(goal.parts)

    def count_goals_intersections(self, goal):
        if isinstance(goal, pddlsim.parser_independent.Literal):
            return 0
        return 1 + sum([self.count_goals_intersections(part) for part in goal.parts])


    def reset_past(self):
        self.last_action = None
        self.last_state = None
        self.past_few_states = collections.deque([], 5)

    def boltzman_value(self, state, action):
        sum_probs = sum([np.exp(value / self.T) for key, value in self.Qtable[state].items()])
        return np.exp(self.Qtable[state][action] / self.T) / sum_probs

    def get_actions_prob(self, state):
        return [self.boltzman_value(state, action) for action in sorted(list(self.Qtable[state].keys()))]


#######################################################################
## this executive runs when -E flag in given.
## decides the next action by the policy file
#######################################################################
class LearnedExecutor(BaseExecutor):
    def __init__(self):
        self.Qtable = {}
        self.planner = None
        self.in_new_domain = False
        self.past_actions = collections.deque([], 5)
        self.last_state = None
        self.rep_count = 0

    def initialize(self, services, sim):
        self.services = services
        self.policy_file = self.services.parser.domain_name + "_" + self.services.parser.problem_name + "_final"
        if os.path.isfile(self.policy_file):
            self.load_table()
        elif self.is_deterministic(self.services.parser.actions):
            self.planner = PlanDispatcher()
            self.planner.initialize(services)
        else:
            self.in_new_domain = True

    def next_action(self):
        if self.services.goal_tracking.reached_all_goals():
            return None

        # if the given domain is deterministic:
        if self.planner:
            return self.planner.next_action()

        current_state = self.services.perception.get_state()
        state_rep = self.represent_state(current_state)
        all_actions = self.services.valid_actions.get()
        actions = [action for action in all_actions if action not in self.past_actions]
        # in case this domain and problem are known:
        if not self.in_new_domain:
            if self.last_state == state_rep:
                self.rep_count += 1
            else:
                self.rep_count = 0
            if len(actions) == 0 or (self.last_state == state_rep and self.rep_count < 5):
                action = self.max_action(state_rep, all_actions)
            else:
                action = self.max_action(state_rep, actions)
        # in case this domain and problem are new:
        else:
            if len(actions) == 0 or self.last_state == state_rep:
                action = random.choice(all_actions)
            else:
                action = random.choice(actions)
        self.last_state = state_rep
        self.past_actions.append(action)
        return action


##############################################
# planner:
##############################################
class PlanDispatcher(Executor):

    def __init__(self):
        super(PlanDispatcher, self).__init__()
        self.steps = []

    def initialize(self, services):
        self.steps = planner.make_plan(services.pddl.domain_path, services.pddl.problem_path)

    def next_action(self):
        if len(self.steps) > 0:
            return self.steps.pop(0).lower()
        return None
