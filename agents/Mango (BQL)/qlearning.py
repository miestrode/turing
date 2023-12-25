# Name: Yehonatan Sofri
# ID:   205433329


import numpy as np
import random
import io_handler
import qtable_handler
import pddlsim.parser_independent as pars


# default values for learning phase
epsilon = 1
alpha = 0.5
gamma = 0.99
r_value = 100
table_postfix = " q_table"
metadata_postfix = " q_metadata"
plan_postfix = " q_plan"


def get_np_array(shape, t):
    a = np.zeros(shape, t, "C")
    return a


def get_num_of_subgoals(services):
    goals = services.parser.goals
    n = 0
    if len(goals) == 1:
        if isinstance(goals[0], pars.JunctorCondition):
            return len(goals[0].parts)
        else:
            n = 1
    else:
        n = len(goals)
    return n


class QLearning:
    def __init__(self, file_name, should_hurry=False):
        self._table = qtable_handler.QTable()
        self._services = None
        self._file_name = file_name
        self.got_to_goal = False
        self.success_counter = 0
        self.plan = []
        self.start_positions = set()
        self.should_hurry = should_hurry

        # for updating table
        self._n_iterations = 0
        self._previous_state_key = 0
        self._previous_action_key = 0
        self._previous_state = None
        self._previous_action = None

        # for handling infinite loops
        self._last_20 = get_np_array(20, int)
        self._last_20_set = set()
        self._last_20_before_last_20 = get_np_array(20, int)
        self._last_20_before_last_20_set = set()
        self._20_list_idx = 0

        # for mapping key to string
        self._string_to_num = {}
        self._num_to_string = {}
        self._counter = 0

    def _save_table(self):
        io_handler.IOHandler.write(
            self._file_name + table_postfix, self._table.get_table()
        )

    def _set_table(self):
        """
        use io_handler to read table and set it in instance variable.
        """
        q_table = io_handler.IOHandler.read(self._file_name + table_postfix)
        if q_table is not None:
            self._table.set_table(q_table)

    def _set_metadata(self):
        """
        metadata variables are counter to help giving unique keys to strings,
        and dictionaries to convert strings to numbers and vice versa.
        use io_handler to get data from file (if exist).
        """
        global epsilon
        file_name = self._file_name + metadata_postfix
        data = io_handler.IOHandler.read(file_name)
        if data is not None:
            self._counter = data["counter"]
            self._num_to_string = data["num_to_string"]
            self._string_to_num = data["string_to_num"]
            self.success_counter = data["success_counter"]
            epsilon = data["epsilon"]
            self.start_positions = data["start_positions"]

    def _set_variables(self, services):
        """
        set data members of object. set q_table using file (if exists).
        :param services:
        """
        self._services = services
        self._set_table()
        self._set_metadata()

    def _update_table_entry(self, s, a, r, next_state):
        """
        reset the value in the Q(s,a) entry.
        :param s: state string as represented in q_table
        :param a: action string as represented in q_table
        :param r: reward (float)
        :param next_state: next state after applying a on s (string)
        """
        next_state_max = self._table.get_max_value_from_state(next_state)
        q_s_a = self._table.get_value(s, a)
        val = ((1 - alpha) * q_s_a) + (alpha * (r + (gamma * next_state_max)))
        self._table.set_entry(s, a, val)

    def _save_metadata(self):
        file_name = self._file_name + metadata_postfix
        metadata = {
            "counter": self._counter,
            "num_to_string": self._num_to_string,
            "string_to_num": self._string_to_num,
            "success_counter": self.success_counter,
            "epsilon": epsilon,
            "start_positions": self.start_positions,
        }
        io_handler.IOHandler.write(file_name, metadata)

    def _save_data(self):
        self._save_table()
        self._save_metadata()

    def save_plan(self):
        """
        this method take the self.plan keys list and make a string list.
        the action keys are saved by the log handler function.
        this plan is saved in a file.
        """
        file_name = self._file_name + plan_postfix
        plan = []
        if self.plan:
            plan.append(self._num_to_string[str(self.plan.pop(0))])
        for key in self.plan:
            action = self._num_to_string[str(key)]
            if plan and action != plan[-1]:
                plan.append(action)
        io_handler.IOHandler.write(file_name, plan)

    def get_plan(self):
        """
        set plan of problem from saved in a file plan.
        set data member to this plan if it exist.
        :return: the plan.
        """
        file_name = self._file_name + plan_postfix
        plan = io_handler.IOHandler.read(file_name)
        if plan is not None:
            self.plan = plan
        return plan

    def _convert_string_to_num(self, string):
        """
        :param string: string representation of state
        :return: int key of string in instance data
        """
        if string in self._string_to_num.keys():
            value = self._string_to_num[string]
        else:
            value = self._counter
            self._string_to_num[string] = value
            self._num_to_string[str(value)] = string
            self._counter += 1
        return value

    def __change_elements_in_state_history(self, state_key):
        """
        helper for self._update_the_past(). get a key of current state.
        and change the data in the lists of 20 last states and 20 beforehand.
        :param state_key:
        :return:
        """
        dumped_from_20 = self._last_20[self._20_list_idx]
        dumped_from_20_before_20 = self._last_20_before_last_20[self._20_list_idx]

        self._last_20_before_last_20[self._20_list_idx] = self._last_20[
            self._20_list_idx
        ]
        self._last_20[self._20_list_idx] = state_key

        return dumped_from_20, dumped_from_20_before_20

    def _update_the_past(self, state_key):
        """
        updates the history of states - 20 last actions and 20 actions before.
        there are 2 lists and 2 sets that help to track the last 40 actions.
        one list is last 20 states agent been in, and a complementary set.
        second list is the 20 states before the 20 state in the first list.
        for this list there's also a complementary set.
        :param state_key - key of current state
        """
        from_20 = None
        from_20_before_20 = None

        if self._n_iterations < 40:
            if self._n_iterations < 20:
                self._last_20_before_last_20[self._20_list_idx] = state_key
                self._last_20_before_last_20_set.add(state_key)
            else:
                self._last_20[self._20_list_idx] = state_key
                self._last_20_set.add(state_key)
        else:
            deleted_keys_tuple = self.__change_elements_in_state_history(state_key)
            from_20 = deleted_keys_tuple[0]
            from_20_before_20 = deleted_keys_tuple[1]

        # if an element was removed from every list
        if from_20 is not None:
            self._last_20_set.add(state_key)
            self._last_20_before_last_20_set.add(from_20)
            if from_20_before_20 not in self._last_20_before_last_20:
                self._last_20_before_last_20_set.remove(from_20_before_20)
            if from_20 not in self._last_20:
                self._last_20_set.remove(from_20)
        self._20_list_idx = (self._20_list_idx + 1) % 20

    def _in_infinite_loop(self):
        """
        check if the agent is in an infinite loop by checking history.
        if the last 20 states are the same as the 20 state beforehand,
        it's a sign for that agent is in a loop.
        :return: True if infinte loop was detected
        """
        counter = 0
        if self._n_iterations < 40:
            return False
        for element in self._last_20_set:
            if element in self._last_20_before_last_20_set:
                counter += 1

        return counter == len(self._last_20_set)

    def _get_best_action(self, state_string):
        """
        use table handler to get the best action in current state.
        :param state_string: is a string representation of current state
        :return: the best action to make in state of all valid actions
        """
        action = None
        va = self._services.valid_actions.get()
        action_key = self._table.get_max_action_from_state(state_string)

        if action_key in self._num_to_string.keys():
            action = self._num_to_string[action_key]

        # action is not in table or is not appliable currently
        if va is None:
            action = None
        elif action is None or action not in va:
            action = self._get_random_action(va)
        return action

    def _get_random_action(self, va=None):
        random_action = None
        if va is None:
            va = self._services.valid_actions.get()
        if va:
            random_action = random.choice(va)
        return random_action

    def add_one_to_success(self):
        """
        adding 1 to counter of successful runs in problem.
        every 20 successfull runs epsilon decrease by 0.1.
        if over 200 successes, epsilon returns to 1.
        :return:
        """
        global epsilon
        self.success_counter += 1
        if self.success_counter % 20 == 0:
            epsilon -= 0.05
        elif self.should_hurry:
            epsilon -= 0.1

    @staticmethod
    def dict_to_string(d):
        """
        dictionary to string function.
        dictionaries with same content but different order get same string.
        :param d: dictionary
        :return: string of dictionary in alphabetical order
        """
        li = []
        keys = sorted(d.keys())
        if keys[0] is "=":
            keys.pop(0)
        for key in keys:
            k = [str(tup) for tup in d[key]]
            k.sort()
            k.insert(0, key)
            li.append(k)
        return str(li)

    def get_reward(self, end):
        if end:
            self.got_to_goal = True
            return r_value
        else:
            return -1

    def get_n_iterations(self):
        return self._n_iterations


class BackwardQLearning(QLearning):
    """
    class for reinforcement learning via backward q learning.
    """

    # dimensions of log matrix
    m = 512
    n = 2

    def __init__(self, file_name, hurry_up=False):
        QLearning.__init__(self, file_name, hurry_up)
        self.__set_log()

    def __set_log(self):
        self.__s_a_log = [get_np_array((BackwardQLearning.m, BackwardQLearning.n), int)]
        self.__r_log = [get_np_array(BackwardQLearning.m, float)]
        self.__i = 0
        self.__k = 0

    def __resize_log(self):
        self.__s_a_log.append(
            get_np_array((BackwardQLearning.m, BackwardQLearning.n), int)
        )
        self.__r_log.append(get_np_array(BackwardQLearning.m, float))
        self.__i = 0
        self.__k += 1

    def __put_numbers_in_log(self, s, a, r):
        """
        get keys of state and action and a reward value and store it in log.
        """
        self.__s_a_log[self.__k][self.__i] = [s, a]
        self.__r_log[self.__k][self.__i] = r
        self.__i += 1

    def __add_to_log(self, state_key, action_key=-1, reward=-1):
        """
        add data of state key, action key and reward to log matrices.
        :param state_key: int key representation of state
        :param action_key: int key representation of action
        :param reward: float
        """
        if self.__i >= BackwardQLearning.m:
            self.__resize_log()
        self.__put_numbers_in_log(state_key, action_key, reward)

    def __reset_to_bad_reward(self):
        """
        change last reward in log to -100
        """
        # setting k and i to last entry in log
        if self.__i is 0:
            i = BackwardQLearning.m - 1
            k = self.__k - 1
        else:
            i = self.__i
            k = self.__k

        self.__r_log[k][i] = r_value * 0.1

    def __handle_deadlock(self, state_key):
        self.__reset_to_bad_reward()
        self.__add_to_log(state_key)
        self.__backward_update_and_save_table()

    def __backward_update_entry(self, next_state_key):
        """
        get key of next state and position in log.
        translate arguments to state and action as represented in q_table.
        update the entry of the specified state and action in log.
        """
        # next_state = self._num_to_string[str(next_state_key)]
        s_a_keys = self.__s_a_log[self.__k][self.__i]
        s_key, a_key = s_a_keys[0], s_a_keys[1]

        self.plan.insert(0, a_key)

        r = self.__r_log[self.__k][self.__i]

        self._update_table_entry(str(s_key), str(a_key), r, next_state_key)

    def __backward_update_and_save_table(self):
        """
        Here's the magic
        """
        # for last row in log - different from others, contain state only
        self.__i -= 1

        # go to previous log table last index
        if self.__i < 0:
            self.__k -= 1
            self.__i = BackwardQLearning.m - 1

        next_state_key = self.__s_a_log[self.__k][self.__i][0]

        self.__i -= 1

        # run on row i of matrix k
        while self.__k >= 0:
            while self.__i >= 0:
                self.__backward_update_entry(next_state_key)
                next_state_key = self.__s_a_log[self.__k][self.__i][0]
                self.__i -= 1
            self.__i = BackwardQLearning.m - 1
            self.__k -= 1
        self._save_data()

    def __update(self, state_key):
        # if it's not 1st iteration, add reward and last state&action to log
        if self._previous_state_key is not self._previous_action_key:
            reward = self.get_reward(self._services.goal_tracking.reached_all_goals())
            self.__add_to_log(
                self._previous_state_key, self._previous_action_key, reward
            )
        self._update_the_past(state_key)

    def initialize(self, services):
        global epsilon
        self._set_variables(services)
        start_key = self.dict_to_string(services.perception.state)
        if start_key not in self.start_positions:
            self.start_positions.add(start_key)
            epsilon = 1

    def next_action(self):
        state_string = QLearning.dict_to_string(self._services.perception.state)
        state_key = self._convert_string_to_num(state_string)

        self.__update(state_key)

        # if is goal state - add last state and backward update
        if self._services.goal_tracking.reached_all_goals():
            self.add_one_to_success()
            self.__add_to_log(state_key)
            self.__backward_update_and_save_table()
            self.save_plan()
            return None

        # choose action, epsilon greedily
        if epsilon >= random.uniform(0, 1):
            current_action = self._get_random_action()
        else:
            current_action = self._get_best_action(str(state_key))

        if current_action is None:
            self.__handle_deadlock(state_key)
            return None

        if self._in_infinite_loop():
            self.__backward_update_and_save_table()
            return None

        # save data for next iteration
        self._previous_state_key = state_key
        self._previous_action_key = self._convert_string_to_num(current_action)

        # for debugging
        self._n_iterations += 1

        return current_action


class QLearningExecutive(QLearning):
    """
    standard q learning class for pddlsim. save table in file every 10 actions.
    """

    def __init__(self, file_name):
        QLearning.__init__(self, file_name)
        self.determinism = True

    def set_determinism(self):
        """
        set a data member to mention if the domain is deterministic or not.
        do it by checking if any action has prob_list key.
        """
        for action in self._services.parser.actions:
            try:
                var = self._services.parser.actions[action].prob_list
                self.determinism = False
                return
            except:
                pass

    def initialize(self, services):
        self._services = services
        self.set_determinism()
        if self.get_plan() is None or not self.determinism:
            self._set_table()
            self._set_metadata()

    def next_action(self):
        action = None

        if self._services.goal_tracking.uncompleted_goals:
            if self.determinism:
                if self.plan:
                    action = self.plan.pop(0)
            else:
                state_string = self.dict_to_string(self._services.perception.state)
                state_key = self._convert_string_to_num(state_string)
                action = self._get_best_action(state_key)

        return action
