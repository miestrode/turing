import random
import sys
import os
import pddlsim.services
from pddlsim.executors.executor import Executor
import pddlsim.planner as planner
from pddlsim.local_simulator import LocalSimulator


class LearningAgent:
    """ docstring for Learning agent that uses Reinforcement learning to achive a policy"""
    def __init__(self):
        self.current_state = None
        self.previous_state = None
        self.action_taken = None
        self.q_table = {}
        self.alpha = 0.2
        self.gama = 0.8
        self.exploitation = 0.8
        self.goals = None
        self.curr_goals_comp = 0
        self.prev_goals_comp = 0
        self.plan = []
        self.track_to_goal = []

    def initialize(self, services):
        try:
            self.plan = planner.make_plan(services.pddl.domain_path, services.pddl.problem_path)
        except:
            if self.plan is None:
                self.plan = []
        self.services = services
        self.goals = self.services.goal_tracking.uncompleted_goals[0].parts
        random.shuffle(self.goals)
        self.current_state = self.services.perception.get_state()
        self.read_q_table()
        self.curr_goals_comp = 0
        self.prev_goals_comp = 0
        self.track_to_goal = []

    def write_q_table(self):
        seq = []
        for state in self.q_table:
            seq.append(state + "~" + str(self.q_table[state]) + '\n')
        with open("policy:" + sys.argv[2] + sys.argv[3], 'w') as file1:
            file1.writelines(seq)

    def read_q_table(self):
        self.q_table.clear()
        if os.path.isfile("policy:" + sys.argv[2] + sys.argv[3]):
            with open("policy:" + sys.argv[2] + sys.argv[3], 'r') as file1:
                for line in file1:
                    pair = line.split("~")
                    if len(pair) > 1:
                        self.q_table[pair[0]] = float(pair[1])

    def next_action(self):
        if self.services.goal_tracking.reached_all_goals():
            if sys.argv[1] == "-L":
                self.update_q()
                self.write_q_table()
            return None

        if sys.argv[1] == "-L":
            self.update_q()
            return self.next_learning_action()
        elif sys.argv[1] == "-E":
            if len(self.plan) > 0:
                return self.plan.pop(0).lower()
            action = self.next_policy_action()
            return action
        else:
            print "phase flag missing"
            return None

    def update_q(self):
        if self.previous_state is not None:
            self.previous_state = self.current_state
            self.current_state = self.services.perception.get_state()
            state_string = self.state_to_string(self.previous_state)
            curr_q = self.get_q(state_string + self.action_taken)
            max_q_of_new_state = self.get_q(self.state_to_string(self.current_state) + self.q_optimal_action())
            new_q = (1 - self.alpha) * curr_q + (self.alpha * (self.get_reward() + self.gama * max_q_of_new_state))
            self.q_table[state_string + self.action_taken] = new_q
            self.track_to_goal.append(state_string + self.action_taken)
        else:
            self.previous_state = self.current_state

    def get_q(self, key):
        q = self.q_table.get(key)
        if q is None:
            q = 0
        return q

    def get_reward(self):
        self.goals_reached_count()
        if self.curr_goals_comp > self.prev_goals_comp:
            r = 1000000 * (100**self.curr_goals_comp)
            self.trim_and_propagate()
            return r
        elif self.curr_goals_comp < self.prev_goals_comp:
            return -1000000 * (100**self.prev_goals_comp)
        else:
            return -100

    def goals_reached_count(self):
        self.prev_goals_comp = self.curr_goals_comp
        reached = 0
        for goal in self.goals:
            if self.services.parser.test_condition(goal, self.current_state):
                reached += 1

        random.shuffle(self.goals)
        self.curr_goals_comp = reached

    def trim_and_propagate(self):
        path = self.track_to_goal
        # Trim
        itr = len(path) - 1
        while itr > 0:
            itr2 = len(self.track_to_goal) - 1
            max_state = None
            max_trim = 0
            max_first_time = 0
            while itr2 > 0:
                state2 = self.track_to_goal[itr2]
                first_time2 = self.track_to_goal.index(state2)
                if itr2 - first_time2 > max_trim:
                    max_state = state2
                    max_trim = itr2 - first_time2
                    max_first_time = first_time2
                itr2 = first_time2 - 1

            if max_trim == 0:
                break
            else:
                state = max_state
                first_time = max_first_time
                for i in range(0, max_trim):
                    path.pop(first_time)
                itr = first_time - 1
            # propagate
            for i in range(len(path) - 1, 0):
                curr_q = self.get_q(path[i -1])
                self.q_table[path[i-1]] = (1 - self.alpha) * curr_q + (self.alpha * (self.gama * self.get_q(path[i])))

    def next_learning_action(self):
        if random.random > self.exploitation:
            self.action_taken = self.random_action()
        else:
            self.action_taken = self.q_optimal_action()
        return self.action_taken

    def random_action(self):
        options = self.services.valid_actions.get()
        if len(options) == 0:
            self.write_q_table()
            return None
        random.shuffle(options)
        action = options[0]
        for option in options:
            if self.q_table.get(self.state_to_string(self.current_state) + option) is None:
                action = option
            return action

    def q_optimal_action(self):
        options = self.services.valid_actions.get()
        if len(options) == 0:
            self.write_q_table()
            best_act = None
        elif len(options) == 1:
            best_act = options[0]

        else:
            random.shuffle(options)
            unexplored = None
            best_act = None
            max_q = 0
            for act in options:
                s = self.state_to_string(self.current_state) + act
                q = self.q_table.get(s)
                if q is None:
                    if unexplored is None:
                        unexplored = act
                elif q > max_q:
                    max_q = q
                    best_act = act

            if best_act is None:
                if unexplored is not None and sys.argv[1] == "-L":
                    best_act = unexplored
                else:
                    best_act = options[0]

        return best_act

    def next_policy_action(self):
        self.current_state = self.services.perception.get_state()
        return self.q_optimal_action()

    def state_to_string(self, state):
        order = frozenset(state)
        string_state = {}
        for sub_state in order:
            grounded = sorted(state[sub_state])
            s = "".join(str(grounded))
            string_state[sub_state] = s
        return str(string_state)


if __name__ == '__main__':

    domain_path = sys.argv[2]
    problem_path = sys.argv[3]
    player = LearningAgent()
    print LocalSimulator().run(domain_path, problem_path, player)
