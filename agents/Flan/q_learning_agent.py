import random
from pddlsim.executors.executor import Executor

HISTORY_LEN = 10


class Q_Learning(Executor):
    def __init__(self, mode, policyfile_name):
        super(Q_Learning, self).__init__()
        self.mode = mode[1]  # mode is either '-L' or '-E'
        self.policytable = {}
        self.init_state = None
        self.prev_state = None
        self.prev_action_name = None
        self.state_history = []
        self.policyfile_name = policyfile_name

    def initialize(self, services):
        self.services = services
        self.init_state = self.services.perception.get_state()
        self.actions_map = {
            action: index
            for index, action in enumerate(sorted(self.services.parser.actions.keys()))
        }
        self.num_actions = len(self.actions_map)
        self.num_remaining_goals = len(self.services.goal_tracking.uncompleted_goals)
        self.achieved_goal = False

        try:
            policyfile = open(self.policyfile_name, "r")
            if len(policyfile.readlines()) == 0:  # POLICYFILE exists but empty
                policyfile.close()
                self.create_policyfile()
            self.load_policyfile()

        except IOError:  # POLICYFILE does not exist
            self.create_policyfile()
            self.load_policyfile()

    def next_action(self):
        # Check if a goal was achieved in previous step
        if (
            len(self.services.goal_tracking.uncompleted_goals)
            < self.num_remaining_goals
        ):
            self.achieved_goal = True
            self.q_learn(
                self.prev_state,
                self.prev_action_name,
                self.get_state_hashed(),
                reward=1000,
                alpha=0.5,
                gamma=0.9,
            )
            self.num_remaining_goals = len(
                self.services.goal_tracking.uncompleted_goals
            )
        else:
            self.achieved_goal = False

        # Check if problem is finished - all goals reached or no more valid actions
        # If finished - update POLICYFILE
        if (
            self.services.goal_tracking.reached_all_goals()
            or len(self.services.valid_actions.get()) == 0
        ):
            if self.mode == "L":  # Learning mode
                self.update_policyfile()
            return None

        if self.get_state_hashed() in self.policytable:
            # Learn with reward -1
            self.q_learn(
                self.prev_state,
                self.prev_action_name,
                self.get_state_hashed(),
                reward=-10,
                alpha=0.5,
                gamma=0.9,
            )
        else:
            # Add current state as a new state in policytable
            self.policytable[self.get_state_hashed()] = [0] * self.num_actions

        if random.random() < 0.2:  # With probability 0.2, do "explore"
            action = self.explore()
        else:  # With probability 0.8, do "exploit"
            action = self.exploit()

        # Save previous state and action, for learning in next iteration
        self.prev_state = self.get_state_hashed()
        self.prev_action_name = action.strip("()").split(" ")[0]

        # Add previous state to history and check for cycles
        self.add_to_history(self.get_state_hashed())
        if len(self.state_history) == HISTORY_LEN and self.check_cycles() > 0:
            # print("Found Cycle: " + str(self.check_cycles()))
            if self.mode == "L":  # Learning mode
                self.update_policyfile()
            if self.mode != "E":
                return None  # Abort run

        return action

    def create_policyfile(self):
        pf = open(self.policyfile_name, "w")
        pf.close()

        return pf

    def load_policyfile(self):
        pf = open(self.policyfile_name, "r")
        for row in pf.readlines():
            row_list = row.split(" ")
            q_values = [float(num) for num in row_list[1:]]
            self.policytable[row_list[0]] = q_values

        pf.close()

    def update_policyfile(self):
        pf = open(self.policyfile_name, "w")
        for state, q_values in self.policytable.iteritems():
            row = str(state) + " " + " ".join(str(num) for num in q_values) + "\n"
            pf.write(row)
        pf.close()

    def get_state_hashed(self):
        cur_state = self.services.perception.get_state()
        hashed_state = self.calc_diff_from_start(cur_state)
        if hashed_state == "":
            hashed_state = "init_state"
        return hashed_state

    def calc_diff_from_start(self, cur_state):
        diff = ""
        for predicate_name, predicate_set in cur_state.items():
            if predicate_name == "=":
                continue
            base_predicate_set = self.init_state[predicate_name]
            set_diff = predicate_set.difference(base_predicate_set)
            if len(set_diff) > 0:
                diff += predicate_name + "_" + str(set_diff)
        return diff.replace(" ", "")

    def add_to_history(self, state):
        self.state_history.append(state)
        if len(self.state_history) > HISTORY_LEN:
            del self.state_history[0]

    def check_cycles(self):
        """
        Check if last states in state_history repeat themselves
        :return: length of cycle if states repeat, 0 otherwise
        """
        for i in range(1, int(len(self.state_history) / 2) + 1):
            cycles = [
                self.state_history[x : x + i]
                for x in range(0, len(self.state_history), i)
            ]
            if [cycles[0]] * len(cycles) == cycles:
                return i
        return 0

    def explore(self):
        actions = self.services.valid_actions.get()
        return random.choice(actions)

    def exploit(self):
        cur_state = self.get_state_hashed()
        actions = self.services.valid_actions.get()
        action_value_list = []
        for action in actions:
            action_name = action.strip("()").split(" ")[0]
            action_index = self.actions_map[action_name]
            action_value = self.policytable[cur_state][action_index]
            action_value_list.append((action, action_value))
        return max(action_value_list, key=lambda x: x[1])[0]

    def q_learn(self, prev_state, action_name, cur_state, reward, alpha, gamma):
        if cur_state not in self.policytable.keys():
            self.policytable[cur_state] = [0] * self.num_actions
        if self.prev_state is not None:
            action_index = self.actions_map[action_name]
            learn_value = alpha * (
                reward
                + gamma * max(self.policytable[cur_state])
                - self.policytable[prev_state][action_index]
            )
            if abs(learn_value) > 1:
                self.policytable[prev_state][action_index] += learn_value
            else:
                self.policytable[prev_state][action_index] += alpha * reward
