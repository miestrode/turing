# Name: Yehonatan Sofri
# ID:   205433329


import pddlsim.parser_independent as prs
import goal_tracking as gt
import valid_actions as va
import qlearning as ql
import io_handler
import random
import copy
import math
import sys

metadata_postfix = " mcts_metadata"
table_postfix = " mcts_table"
plan_postfix = " mcts_plan"
fixed_epoch_duration = None
c = 2
rollout_iterations = 100
n_simulations = 5


class MonteCarloTreeSearch:
    def __init__(self, file_name):
        self.string_to_num = {}
        self.num_to_string = {}
        self.table = {}
        self.plan = []
        self.index_counter = long(0)
        self.N = long(0)
        self.got_to_goal = False
        self.services = None
        self.sub_goals = None
        self.determinism = None
        self.value = 1
        self.goal_state = -1
        self.file_name = file_name

    def save_table(self):
        file_name = self.file_name + table_postfix
        io_handler.IOHandler.write(file_name, self.table)

    def save_metadata(self):
        file_name = self.file_name + metadata_postfix
        metadata = {
            "N": self.N,
            "determinism": self.determinism,
            "num_to_string": self.num_to_string,
            "string_to_num": self.string_to_num,
            "counter": self.index_counter,
            "got_to_goal": self.got_to_goal,
            "goal_state": self.goal_state,
            "value": self.value
        }
        io_handler.IOHandler.write(file_name, metadata)

    def save_data(self):
        self.save_metadata()
        self.save_table()
        if self.got_to_goal or self.determinism:
            self.save_plan()

    def save_plan(self):
        """
        make a list of actions to goal state and save in a file
        """
        self.plan = []
        file_name = self.file_name + plan_postfix
        if self.determinism:
            keys_plan = self.make_best_moves_list()
            for key in keys_plan:
                action = self.num_to_string[str(key)]
                self.plan.append(action)
        elif self.got_to_goal:
            s_key = self.goal_state
            parent = self.table[str(s_key)]['p']

            while parent is not None:
                p_string = str(parent)
                best_prob = 0
                best_action = None
                for key in self.table[p_string].keys():
                    if self.is_action(key):
                        for tmp_set in self.table[p_string][key]:
                            if tmp_set[0] == s_key and tmp_set[1] > best_prob:
                                best_action = key
                                best_prob = tmp_set[1]

                self.plan.insert(0, best_action)
                s_key = parent
                parent = self.table[str(s_key)]['p']
        if self.plan:
            io_handler.IOHandler.write(file_name, self.plan)

    def set_table(self):
        """
        get tree of domain using file system.
        """
        file_name = self.file_name + table_postfix
        my_table = io_handler.IOHandler.read(file_name)
        if my_table is not None:
            self.table = my_table

    def set_subgoals(self):
        if len(self.services.parser.goals) is 1:
            if isinstance(self.services.parser.goals[0], prs.Literal):
                self.sub_goals = self.services.parser.goals
            else:
                self.sub_goals = self.services.parser.goals[0].parts
        else:
            self.sub_goals = [goal for goal in self.services.parser.goals]

    def set_metadata(self):
        """
        get additional data about a domain using file system.
        """
        file_name = self.file_name + metadata_postfix
        data = io_handler.IOHandler.read(file_name)
        if data is not None:
            self.index_counter = data["counter"]
            self.num_to_string = data["num_to_string"]
            self.string_to_num = data["string_to_num"]
            self.determinism = data["determinism"]
            self.N = data["N"]
            self.got_to_goal = data["got_to_goal"]
            self.goal_state = data["goal_state"]
            self.value = data["value"]

    def set_determinism(self):
        """
        set a data member to mention if the domain is deterministic or not.
        """
        if self.determinism is None:
            self.determinism = True
            for action in self.services.parser.actions:
                try:
                    var = self.services.parser.actions[action].prob_list
                    self.determinism = False
                    return
                except:
                    pass

    def set_variables(self, services):
        """
        set all relevant data for the class to run MCTS algorithm.
        :param services: from simulator
        """
        self.services = services
        self.set_subgoals()
        self.set_metadata()
        self.set_table()
        self.set_determinism()
        self.gt = gt.GoalTracking(services.parser, services.perception)

    def get_plan(self):
        """
        read plan from file and return a list of
        :return:
        """
        plan = None
        file_name = self.file_name + plan_postfix
        plan = io_handler.IOHandler.read(file_name)
        if plan is not None:
            self.plan = plan
        return plan

    def initialize(self, services):
        self.set_variables(services)

    def get_state_dict_hash(self, d):
        """
        hash a dictionary so it'll have a matching hash.
        save dictionary in num_to_string.
        :param d: dictionary of a state.
        :return: a long int key that represents the action
        """
        state_string = ql.QLearning.dict_to_string(d)
        if state_string not in self.string_to_num.keys():
            d = copy.deepcopy(d)
            self.string_to_num[state_string] = self.index_counter
            self.num_to_string[str(self.index_counter)] = d
            self.index_counter += 1
        return self.string_to_num[state_string]

    def get_action_string_hash(self, a):
        """
        make a hash of given action string. store it in class data.
        :param a: string if an action
        :return: a long int key that represents the action
        """
        if a not in self.string_to_num.keys():
            self.string_to_num[a] = self.index_counter
            self.num_to_string[str(self.index_counter)] = a
            self.index_counter += 1
        return self.string_to_num[a]

    def get_better_action(self, next_state, mx, t, action_key, action_to_max):
        next_s_str = str(next_state)
        if mx is None or t < self.table[next_s_str]['t']:
            return next_state, self.table[next_s_str]['t'], action_key
        return mx, t, action_to_max

    def make_action_list_from_goal(self):
        """
        build a plan from initial state to goal state.
        :return: list of action keys to get to goal
        """
        l = []
        s_key = self.goal_state
        parent_key = self.table[str(s_key)]['p']

        while parent_key is not None:
            parent_str = str(parent_key)
            for k in self.table[parent_str].keys():
                if self.is_action(k) and self.table[parent_str][k] == s_key:
                    l.insert(0, k)
                    s_key = parent_key
                    parent_key = self.table[str(parent_key)]['p']
                    break
        return l

    def make_best_moves_list(self):
        """
        run on each level of the Monte Carlo tree and take the action that
        has made the maximal reward. reward is saved in key 't' of each state.
        :return a list of moves to get to goal state
        """
        if self.got_to_goal:
            return self.make_action_list_from_goal()
        state_set = {0L}
        s_key = 0L
        l = []
        v_a = va.ValidActions(self.services.parser, self.services.pddl,
                              self.services.perception)
        while not self.is_leaf(s_key) and s_key is not None:
            state_set.add(s_key)
            mx = None
            action_to_max = None
            t = 0
            s_string = str(s_key)

            valid_action = v_a.get(self.num_to_string[s_string])
            if len(valid_action) > len(self.num_to_string[s_string].keys()) - 3 \
                    or ('v' in self.num_to_string[s_string].keys() and
                        len(valid_action) > len(self.num_to_string[s_string].keys()) - 4):
                for action in valid_action:
                    action_key = self.get_action_string_hash(action)
                    action_str = str(action_key)

                    if action_str in self.table[s_string].keys() \
                            and self.table[s_string][action_str] not in state_set:
                        mx, t, action_to_max = \
                            self.get_better_action(
                                self.table[s_string][action_str], mx, t,
                                action_key, action_to_max)
                    else:
                        state_copy = copy.deepcopy(self.num_to_string[s_string])
                        self.apply_action_to_state(action, state_copy)
                        next_s_key = self.get_state_dict_hash(state_copy)
                        action_key = self.get_action_string_hash(action)
                        next_s_str = str(next_s_key)
                        if next_s_str in self.table.keys() \
                                and s_key is not self.table[next_s_str]['p'] \
                                and s_key is not next_s_key \
                                and next_s_key not in state_set:
                            mx, t, action_to_max = self.get_better_action(
                                next_s_key, mx, t, action_key, action_to_max
                            )
            else:
                for k in self.table[s_string].keys():
                    if self.is_action(k):
                        mx, t, action_to_max = self.get_better_action(
                            self.table[s_string][k], mx, t, k, action_to_max)
            s_key = mx
            l.append(action_to_max)
        return l

    def next_action(self):
        """
        for pddl simulator.
        :return: None after making enough iterations of MCTS algorithm.
        """
        s = self.get_state_dict_hash(self.services.perception.state)
        self.add_new_state(s, None)
        self.tree_search_iteration(s)
        return None

    def increase_value(self):
        """
        add 1 to the visited number of node.
        described in key 'v' of each node.
        """
        if 'v' in self.table['0']:
            self.value = self.table['0']['v']
            self.value += 1
        else:
            self.value = 1

    def tree_search_iteration(self, root):
        """
        the main loop of the MCTS algorithm
        :param root: initial state
        """
        to_simulate = True
        if self.is_leaf(root):
            self.expand(root)

        if 'v' in self.table['0'].keys() and \
                self.table['0']['v'] == self.value:
            self.increase_value()
            self.save_data()

        leaf = self.select_node(root)
        if leaf is not None:
            leaf_str = str(leaf)
            # if leaf was visited
            if self.table[leaf_str]['n'] > 0:
                if 'v' not in self.table[leaf_str].keys():
                    self.expand(leaf)
                    to_simulate = False
                self.mark_as_expanded(leaf)
            else:
                to_simulate = True

            if to_simulate:
                simulation_result = self.simulate(leaf)
                self.backpropagate(leaf, simulation_result)

        self.save_data()

    def all_children_visited(self, parent_key):
        """
        return true if all children of node were visited.
        :param parent_key: a key of a node in the table
        :return: True if all children were visited, o.w. return False.
        """
        parent_str = str(parent_key)
        t = 0
        c = 0

        if parent_key is None:
            return False
        for key in self.table[parent_str]:
            if self.is_action(key):
                if self.determinism:
                    t += 1
                    tmp_state = self.table[parent_str][key]
                    tmp_state_str = str(tmp_state)
                    if 'v' in self.table[tmp_state_str].keys() \
                            and self.table[tmp_state_str]['v'] == self.value:
                        c += 1
                else:
                    li = list(self.table[parent_str][key])
                    for pair in li:
                        t += 1
                        tmp_state_str = str(pair[0])
                        if 'v' in self.table[tmp_state_str].keys() \
                                and self.table[tmp_state_str]['v'] == self.value:
                            c += 1
        return t == c

    def add_1_to_v(self, key):
        key_str = str(key)
        if 'v' in self.table[key_str].keys():
            self.table[key_str]['v'] += 1
        else:
            self.table[key_str]['v'] = 1

    def mark_as_expanded(self, leaf_key):
        """
        add 'v' key to node if was visited.
        add 'v' to every node that all it's children are merked with 'v'.
        :param leaf_key: key of lead in tree
        :return:
        """
        if leaf_key is None:
            return

        if self.is_leaf(leaf_key):
            self.add_1_to_v(leaf_key)
        else:
            return

        while (leaf_key is not None) and self.all_children_visited(self.table[str(leaf_key)]['p']):
            leaf_key = self.table[str(leaf_key)]['p']
            self.add_1_to_v(leaf_key)

    def is_leaf(self, node):
        """
        check if a specific node (key of state in the table is a leaf or not).
        a node is a leaf if it consists of only 3 keys in it's own dictionary.
        :param node: number of state in the table
        :return: True if node is a leaf.
        """
        if isinstance(node, long):
            node = str(node)
        if node in self.table.keys():
            if len(self.table[node].keys()) == 3:
                return True
            elif len(self.table[node].keys()) == 4 and 'v' in self.table[node].keys():
                return True
        return False

    def is_action(self, key):
        """
        get a key and return true if it represents an action key.
        that is, key is not 'p', 't' or 'n'. which are in every value.
        :param key: key in the table
        :return: true if key is a key of action
        """
        try:
            int(key)
            return True
        except ValueError:
            return False

    def get_uct(self, state_dict):
        """
        calculate the UCT of a state
        :param state_dict: dictionary of a state from the table
        :return:
        """
        ni = state_dict['n']

        if ni == 0:
            return sys.maxint

        vi = state_dict['t'] / ni
        parent_key = state_dict['p']
        ln_n = math.log(self.table[str(parent_key)]['n'])
        return vi + (math.sqrt(c * ln_n / ni))

    def compare_uct_prob_helper(self, pair, best_uct, best):
        """
        compare between 2 states by comparing uct * probability
        :param pair: tuple of state key and probability
        :param best_uct: uct result of current best node
        :param best: current best state to go to
        :return: the state and ucb1 of the higher state ucb1
        """
        state = pair[0]
        state_string = str(state)
        s_ucb1 = self.get_uct(self.table[state_string])

        if best is None:
            return state, s_ucb1

        best_string = str(best)
        s_n = self.table[state_string]['n']
        b_n = self.table[best_string]['n']
        s_t = self.table[state_string]['t']
        b_t = self.table[best_string]['t']

        # if both state were simulated at least 20 times,
        # return state with more value
        if s_n > 20 and b_n > 20:
            if s_t / s_n > b_t / b_n:
                return state, s_ucb1
            else:
                return best, best_uct

        # multiply in the probability to get to this state
        s_ucb1 *= pair[1]
        if s_ucb1 > best_uct:
            return state, s_ucb1
        return best, best_uct

    def get_better_state_prob(self, best, best_ucb1, value):
        """
        compare between 2 inputs and return the more visit desired state.
        meant for non deterministic problem
        :param best: current best node to visit
        :param value: a node to compare with best node
        :param best_ucb1: ucb1 value of current best node to visit
        :return: tuple of the better node from the two and it's ucb1 value
        """
        li = list(value)
        for pair in li:
            s_str = str(pair[0])
            if not ('v' in self.table[s_str].keys()
                    and self.table[s_str]['v'] == self.value):
                best, best_ucb1 = self.compare_uct_prob_helper(pair, best_ucb1, best)
        return best, best_ucb1

    def get_better_state_deter(self, best, best_ucb1, value):
        """
        compare between 2 inputs and return the more visit desired state.
        meant for deterministic problem
        :param best: current best node to visit
        :param best_ucb1: ucb1 result of current best node
        :param value: a node to compare with best node
        :return: the better node from the two
        """
        best_str = str(best)
        val_str = str(value)
        val_uct = self.get_uct(self.table[val_str])

        if best is None:
            return value, val_uct

        s_n = self.table[val_str]['n']
        b_n = self.table[best_str]['n']
        s_t = self.table[val_str]['t']
        b_t = self.table[best_str]['t']

        if self.table[best_str]['n'] == 0:
            return best, best_ucb1
        elif self.table[val_str]['n'] == 0:
            return value, val_uct
        elif s_n > 20 and b_n > 20 and s_t != 0 and b_t != 0:
            if s_t / s_n > b_t / b_n:
                return value, val_uct
            else:
                return best, best_ucb1
        else:
            if best_ucb1 > val_uct:
                return best, best_ucb1
            return value, val_uct

    def get_best_child(self, node):
        """
        iterate on all possible actions of state and get the best son.
        using helper method that choose by UCT.
        :param node: parent node
        :return: key of most promising child of input node
        """
        best = None
        best_ucb1 = 0
        node_name = str(node)
        keys = self.table[node_name].keys()
        for key in keys:
            if self.is_action(key):
                value = self.table[node_name][key]
                if self.determinism and ('v' not in self.table[str(value)].keys()
                                         or self.table[str(value)]['v'] < self.value):
                    best, best_ucb1 = self.get_better_state_deter(best, best_ucb1, value)
                elif not self.determinism:
                    best, best_ucb1 = self.get_better_state_prob(best, best_ucb1, value)
        return best

    def select_node(self, node):
        """
        method for the selection phase in the algorithm.
        go down the best sub tree and return a lead based on the UCB1.
        :param node: number of state in the table
        :return: node
        """
        while not self.is_leaf(node):
            node_str = str(node)
            if 'v' in self.table[node_str].keys() \
                    and self.table[node_str]['v'] == self.value:
                break
            node = self.get_best_child(node)
            if not node:
                return None

        # in case no children are present / node is terminal
        return node

    def add_new_state(self, hash_num, parent):
        """
        make a new node in the tree/ new entry in the table.
        :param hash_num: key of state
        :param parent: key of parent state
        """
        hash_num_str = str(hash_num)
        if hash_num != parent and hash_num_str not in self.table:
            self.table[hash_num_str] = {
                'p': parent,
                'n': 0,
                't': 0
            }

    def add_probabilistic_action(self, state_key, action_key, next_state_key,
                                 prob):
        """
        add an action to dictionary of state
        :param state_key: key of state in table
        :param action_key: key of possible action from state
        :param next_state_key: key of state' when applying action on state
        :param prob: probability of action
        :return:
        """
        if state_key == next_state_key \
                or self.table[str(next_state_key)]['p'] is not state_key:
            return
        state_key_string = str(state_key)
        s = (next_state_key, prob)
        if action_key in self.table[state_key_string].keys():
            self.table[state_key_string][action_key].add(s)
        else:
            self.table[state_key_string][action_key] = {s}

    def apply_action_to_state(self, action_sig, state_dict, idx=0):
        """
        applying input action on input state dictionary. change input state.
        notice between deterministic domain and probabilistic domain.
        :param action_sig: string of grounded action
        :param state_dict: dictionary of state
        :param idx: number of effect - relevant to probabilistic actions.
        """
        action_name, param_names = self.services.parser.parse_action(action_sig)
        if action_name.lower() == 'reach-goal':
            return state_dict
        action = self.services.parser.actions[action_name]
        params = map(self.services.parser.get_object, param_names)

        param_mapping = action.get_param_mapping(params)

        if self.determinism:
            for (predicate_name, entry) in action.to_delete(param_mapping):
                predicate_set = state_dict[predicate_name]
                if entry in predicate_set:
                    predicate_set.remove(entry)

            for (predicate_name, entry) in action.to_add(param_mapping):
                state_dict[predicate_name].add(entry)
        else:
            for (predicate_name, entry) in action.to_delete(param_mapping, idx):
                predicate_set = state_dict[predicate_name]
                if entry in predicate_set:
                    predicate_set.remove(entry)

            for (predicate_name, entry) in action.to_add(param_mapping, idx):
                state_dict[predicate_name].add(entry)

    def expand_deterministically(self, leaf_node_key):
        """
        expand a leaf to all children state (from valid actions).
        this method is relevant for deterministic domains.
        :param leaf_node_key: the node to expand
        """
        v_a = va.ValidActions(self.services.parser, self.services.pddl,
                              self.services.perception)
        leaf_node_string = str(leaf_node_key)
        state_dict = self.num_to_string[leaf_node_string]

        for action in v_a.get(state_dict):
            action_key = self.get_action_string_hash(action)
            state_copy = copy.deepcopy(state_dict)
            self.apply_action_to_state(action, state_copy)
            hash_num = self.get_state_dict_hash(state_copy)
            self.add_new_state(hash_num, leaf_node_key)
            if hash_num != leaf_node_key and \
                    self.table[str(hash_num)]['p'] == leaf_node_key:
                self.table[leaf_node_string][str(action_key)] = hash_num

    def apply_prob_action_and_add_to_table(self, leaf_node_key, action_string,
                                           state_dict, action_key):
        """
        applying an action with a probability to a state and add state to tree.
        doing it by simulating all possible states from this action.
        :param leaf_node_key: the leaf node to simulate actions from.
        :param action_string: string of an action from state
        :param state_dict: dictionary of state, as represented in pddlsim.
        :param action_key: hash key of action
        """
        i = 0
        action_name, param_names = \
            self.services.parser.parse_action(action_string)
        while i < len(self.services.parser.actions[action_name].prob_list):
            state_copy = copy.deepcopy(state_dict)
            self.apply_action_to_state(action_string, state_copy, i)
            hash_num = self.get_state_dict_hash(state_copy)
            self.add_new_state(hash_num, leaf_node_key)
            prob = self.services.parser.actions[action_name].prob_list[i]
            self.add_probabilistic_action(leaf_node_key,
                                          action_key, hash_num, prob)
            i += 1

    def expand_probabilistically(self, leaf_node_key):
        """
        expand a leaf to all children state (from valid actions).
        this method is relevant for probabilistic domains.
        :param leaf_node_key: the node to expand
        """
        v_a = va.ValidActions(self.services.parser, self.services.pddl,
                              self.services.perception)
        state_dict = self.num_to_string[str(leaf_node_key)]
        for action in v_a.get(state_dict):
            state_copy = copy.deepcopy(state_dict)
            action_key = self.get_action_string_hash(action)
            self.apply_prob_action_and_add_to_table(leaf_node_key, action,
                                                    state_copy, action_key)

    def expand(self, leaf_node_key):
        """
        this method execute the "expand" procedure of MCTS algorithm.
        if it's node a goal state - expand it subtree using helper methods.
        :param leaf_node_key: the node to expand
        """
        state = self.num_to_string[str(leaf_node_key)]
        if self.gt.reached_all_goals(state):
            return

        if self.determinism:
            self.expand_deterministically(leaf_node_key)
        else:
            self.expand_probabilistically(leaf_node_key)

    def count_goals_in_state(self, state):
        """
        use pddlsim to count number of made goals in input state.
        :param state: a dictionary of state as represented in pddlsim.
        :return: number of completed goals.
        """
        counter = 0
        for goal in self.sub_goals:
            if goal.test(state):
                counter += 1
        return counter

    def rollout(self, state, leaf_key):
        """
        make a number of actions as defined in rollout_iteration global var.
        simulate actions starting from input state
        :param state: starting state dictionary
        :param leaf_key: long, number of leaf the rollout go from
        :return: number of goals in final state
        """
        v_a = va.ValidActions(self.services.parser, self.services.pddl,
                              self.services.perception)
        state_copy = copy.deepcopy(state)
        i = 0
        completed = self.count_goals_in_state(state_copy)
        completed_before = completed

        if len(self.sub_goals) == completed:
            self.got_to_goal = True
            self.goal_state = leaf_key
            return float(completed)

        while i < rollout_iterations and completed_before <= completed:
            valid_actions = v_a.get(state_copy)

            if valid_actions:
                action = random.choice(valid_actions)
                self.apply_action_to_state(action, state_copy)
                completed_before = completed
                completed = self.count_goals_in_state(state_copy)
            else:
                return float(-1)
            i += 1
        if completed < completed_before:
            completed = completed_before
        return float(completed)

    def simulate(self, leaf_key):
        """
        make a sample of rollouts as defined in n_simulations global variable.
        :param leaf_key: key of starting state
        :return: sample mean value of simulations
        """
        leaf_name = str(leaf_key)
        state = self.num_to_string[leaf_name]
        i = 0
        result = 0
        while i < n_simulations:
            result += self.rollout(state, leaf_key)
            i += 1
        return result

    def backpropagate(self, leaf_key, simulation_result):
        """
        execute the backpropagation procedure of MCTS algorithm.
        :param leaf_key: the node to start the procedure with
        :param simulation_result: reward that was given in the simulation
        """
        self.N += 1
        node_name = str(leaf_key)

        while node_name != 'None':
            self.table[node_name]['t'] += simulation_result
            self.table[node_name]['n'] += 1
            node_name = str(self.table[node_name]['p'])


class MctsExecutive(MonteCarloTreeSearch):
    """
    an executive for a plan learned by Monte-Carlo Tree Search algorithm.
    """
    def __init__(self, file_name):
        MonteCarloTreeSearch.__init__(self, file_name)
        self.last_state = None
        self.last_action = None

    def get_best_node_not_child(self, valid_actions, state_dict, state_string):
        """
        check from given state, what is the best action to take that is not
        an edge in the state node in the tree.
        this kind of action doesn't always exist.
        :param valid_actions: list of valid actions from current state
        :param state_dict: dictionary of state
        :param state_string: string representation of state
        :return: tuple of best action and it's value
        """
        best_move = None
        best_move_value = 0

        for action in valid_actions:
            action_key = self.get_action_string_hash(action)
            action_name = action[1:-1].split()[0]
            if action_key not in self.table[state_string].keys():
                prob_list = self.services.parser.actions[action_name].prob_list
                for i in range(0, len(prob_list)):
                    state_copy = copy.deepcopy(state_dict)
                    goals_before = self.count_goals_in_state(state_copy)
                    self.apply_action_to_state(action, state_copy, i)
                    goals_after = self.count_goals_in_state(state_copy)
                    s_key = self.get_state_dict_hash(state_copy)
                    s = str(s_key)
                    if s in self.table.keys():
                        tmp_s_value = self.table[s]['t'] / self.table[s]['n']
                        tmp_s_value *= prob_list[i]
                        if (best_move is None or best_move_value < tmp_s_value) \
                                and s_key != self.table[state_string]['p'] \
                                and s != state_string \
                                and goals_before <= goals_after:
                            best_move = action_key
                            best_move_value = tmp_s_value
        return best_move, best_move_value

    def get_best_move_prob(self):
        """
        check what is current state and return the best action to get to goal.
        given the data in the tree.
        :return: best action key from current state
        """
        state_dict = self.services.perception.state
        state_string = str(self.get_state_dict_hash(state_dict))
        goals_before = self.count_goals_in_state(state_dict)

        valid_actions = self.services.valid_actions.get()
        best_move, best_move_value = self.get_best_node_not_child(
            valid_actions, state_dict, state_string)

        for key in self.table[state_string].keys():
            if self.is_action(key):
                for tup in self.table[state_string][key]:
                    next_state, probability = tup[0], tup[1]
                    next_state_str = str(next_state)
                    if self.table[next_state_str]['n'] == 0:
                        continue
                    next_state_dict = self.num_to_string[next_state_str]
                    goals_after = self.count_goals_in_state(next_state_dict)
                    tmp_state_value = self.table[next_state_str]['t'] \
                                      / self.table[next_state_str]['n']
                    tmp_state_value *= probability
                    if best_move is None or best_move_value < tmp_state_value \
                            and goals_before <= goals_after:
                        best_move = key
                        best_move_value = tmp_state_value
        return best_move

    def initialize(self, services):
        self.services = services
        self.set_determinism()
        if not self.determinism:
            self.set_variables(services)
        elif not self.plan:
            self.get_plan()

    def next_action(self):
        action = None

        if self.services.goal_tracking.uncompleted_goals:
            if self.determinism:
                if self.plan:
                    action = self.plan.pop(0)
            else:
                a_key = self.get_best_move_prob()
                if a_key is not None:
                    action = self.num_to_string[str(a_key)]

        return action
