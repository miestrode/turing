import copy
import itertools
import sys
import random
import os.path
import json
import ast
import time

import customized_valid_actions

from pddlsim import planner
from pddlsim.local_simulator import LocalSimulator
from pddlsim.executors.executor import Executor
from pddlsim.parser_independent import Action

# input
input_flag = sys.argv[1]
domain = sys.argv[2]
problem = sys.argv[3]

# states for state machine
DETERMINISTIC = 0
ND = 1  # nondeterministic
WANDER = 2  # nondeterministic without a policy


class ImprovingExecutor(Executor):
    def __init__(self):
        super(ImprovingExecutor, self).__init__()

    def initialize(self, services):
        self.services = services
        self.previous = None  # action
        self.suspect = {}  # hidden predicate discoveries
        self.explored = []
        self.plan = None
        self.has_policy = False
        self.solved = []
        self.pre_solved = None
        self.closed = []
        self.dfstime = 10
        self.task_path = self.services.parser.problem_name + "_MODEL.json"
        self.wander_steps = 1
        self.wander_limit = 1
        self.iterative_depth = 0
        self.STATE = DETERMINISTIC  # optimistic first
        self.subgoals = None

        if os.path.isfile(self.task_path):  # get previous data
            task_file = open(self.task_path, 'r')
            data = ast.literal_eval(json.dumps(json.loads(task_file.read())))
            self.suspect = data["suspect"]  # hidden knowledge
            self.solved = data["solved"]
            if input_flag == "-L":
                self.pre_solved = data["solved"]
            self.closed = data["closed"]
            task_file.close()

    def next_action(self):
        current_state = self.services.perception.get_state()
        # convert state to json form
        s = self.services.parser.copy_state(current_state)
        for pred in s:
            s[pred] = list(s[pred])

        if self.previous is not None:  # can update data after action executed
            self.update_model(current_state)

        if self.services.goal_tracking.reached_all_goals():  # reached goal
            if input_flag == "-L" and self.pre_solved and self.pre_solved == self.solved:#end learning for nndeterministic
                exit(128)
            return None
        else:  # update subgoals?
            new_subgoals = self.get_uncomplete_subgoals(current_state, self.services.goal_tracking.uncompleted_goals[0])
            if self.subgoals and len(new_subgoals) < len(self.subgoals): # found subgoal(s)
                self.solved.append([self.hash_state(self.previous[0]), self.previous[1]])  # add action that lead to subgoal
            self.subgoals = new_subgoals

        if self.STATE == DETERMINISTIC:  # i.e. able to use planner
            if not self.plan:  # try to make a plan
                self.plan = planner.make_plan(self.services.parser.domain_path, self.services.parser.problem_path)
            if not self.plan:  # plan cannot be found by planner->change state
                self.STATE = ND
            else:
                if input_flag == "-L": # no further learning required
                    exit(128)
                a = self.plan.pop(0).lower()
                # save previous state and all possible next states
                self.previous = (s, a)
                self.possible_states = self.get_successor_states(current_state, a)  # states
                return a

        stateid = self.hash_state(current_state)
        if self.STATE == ND:
            if not self.has_policy or stateid not in self.solved:  # try to make policy
                result = self.make_policy(current_state, self.services.goal_tracking.uncompleted_goals[0], self.solved, self.closed)
                # save policy results for future use
                task_file = open(self.task_path, 'w')
                task_file.write(json.dumps({"suspect": self.suspect, "solved": self.solved, "closed": self.closed}))
                task_file.close()
                if result == 3 or result == 0:  # unknown if reaches goal or closed
                    self.STATE = WANDER
                    self.has_policy = False
                else:  # solved
                    self.has_policy = True
            if self.has_policy:
                options = [x for x in self.solved if isinstance(x, list) and stateid in x]
                a = random.choice(options)[1]
                # save previous state and all possible next states
                self.previous = (s, a)
                self.possible_states = self.get_successor_states(current_state, a)  # states
                return a

        if self.STATE == WANDER:  # pick random action while avoiding bad ones
            if stateid in self.solved:  # state is solved,no need to wander-got policy from this point
                # try to make policy from previous state if not labeled
                pre_s = self.previous[0]
                if self.hash_state(pre_s) not in self.solved:
                    self.search_state(current_state, self.services.goal_tracking.uncompleted_goals[0], self.solved,
                                      self.closed, timebound=time.time() + 1)
                # pick a solved action
                options = [x for x in self.solved if isinstance(x, list) and stateid in x]
                self.STATE = ND
                self.has_policy = True
                a = random.choice(options)[1]
                # save previous state and all possible next states
                self.previous = (s, a)
                self.possible_states = self.get_successor_states(current_state, a)  # states
                return a

            if self.wander_steps == 1:  # try policy again next time(last wander step)
                self.STATE = ND
            else:
                self.wander_steps -= 1

            if stateid not in self.explored:  # unexplored
                self.explored.append(stateid)
                if len(self.explored) > 5:
                    self.explored.pop(0)
            else:  # recently explored
                self.explored.remove(stateid)
                self.explored.append(stateid)
            actions = self.services.valid_actions.get()
            if not actions:  # FAIL
                return None
            for a in actions:
                if [stateid, a] in self.solved:  # next action is solved
                    self.solved.append(stateid)
                    return a

            not_closed = [x for x in actions if [stateid, x] not in self.closed]
            if not_closed:  # action 'safe' to take(might be unknown)
                a = random.choice(not_closed)
                # save previous state and all possible next states
                self.previous = (s, a)
                self.possible_states = self.get_successor_states(current_state, a)  # states
                return a
            # no 'safe' actions->search new states
            unexplored = []
            for action in actions:  # check all effects?
                effects = self.get_successor_states(current_state, action)
                for i, effect in enumerate(effects):
                    if self.hash_state(effect) not in self.explored:
                        unexplored.append(action)
            ideal = [x for x in unexplored if [stateid, x] not in self.closed]
            if ideal:  # 'safe' and unexplored
                a = random.choice(ideal)
            # risk to find new states
            elif unexplored:
                a = random.choice(unexplored)
            else:
                a = random.choice(actions)  # all explored and closed
            # save previous state and all possible next states
            self.previous = (s, a)
            self.possible_states = self.get_successor_states(current_state, a)  # states
            return a
        return None  # fail..

    def make_policy(self, si, goal, solved=[], closed=[]):
        d = 0
        start_time = time.time()
        # try normal dfs - good for small problems..
        can_solve = self.search_state(si, goal, solved, closed, [], 500,start_time + self.dfstime)  # timeout problem for big domains!!!
        if can_solve != 3:  # result is known,no need to check farther
            return can_solve
        else:
            self.dfstime /= 2  # spend less time on dfs next time
        start_time = time.time()
        while True:
            can_solve = self.search_state(si, goal, solved, closed, [], d, start_time + 1)  # limit running time??
            if can_solve != 3:  # result is known,no need to check farther
                self.wander_limit = 1
                self.wander_steps = 1
                break
            if time.time() - start_time >= 1:  # timeout
                if self.wander_limit < 550:
                    self.wander_limit *= 2  # spend more time in wander
                self.wander_steps = self.wander_limit
                return 3  # unknown
            d += 1
        return can_solve

    def search_state(self, state, goal, solved=[], closed=[], expended=[], depth=30, timebound=0):  # recursive function
        if timebound - time.time() <= 0:  # timeout
            return 3  # unknown
        stateid = self.hash_state(state)
        if stateid in solved: return 1
        if stateid in closed: return 0
        if stateid in expended:  # seen the state before but not decided yet -> this is a loop!
            return 2  # loop
        expended.append(stateid)

        # leaf state is solved if goal state
        if self.services.parser.test_condition(goal, state):
            solved.append(stateid)
            return 1  # solved
        elif len(self.get_uncomplete_subgoals(state, goal)) < len(self.subgoals):  # found new subgoal
            return 1  # pretend state is solved

        # get all valid actions that are not labeled yet
        actions = customized_valid_actions.CustomizedValidActions(self.services.parser, self.services.perception).get(state)
        # leaf state is closed if no successor and not goal
        if not actions:
            closed.append(stateid)
            return 0  # closed

        # check if more recursion allowed
        if depth == 0:  # could not figure out the path in a reasonable amount of time..
            return 3  # unknown

        action_unknown = False
        for action in actions:
            # action 'layer':
            if [stateid, action] in closed:  # action is irrelevant-continue
                continue
            # recursive call on action effects
            i = 0
            loops = 0
            unknown = 0
            while True:  # go over all effects of the action

                next_state = self.get_successor_state(state, action, i)
                if not next_state:  # explored all effects
                    break

                # check if hidden predicate is generated by current state+action and update accordingly
                event = str(self.hash_state(next_state))
                if self.suspect and event in self.suspect:
                    x = self.suspect[event]
                    add = x[0].copy()
                    delete = x[1].copy()
                    for key in add.keys():
                        add[key] = set([tuple(x) for x in add[key]])  # translate from json format
                        if key in next_state:
                            next_state[key] = next_state[key].union(add[key])
                        else:  # new predicate type
                            next_state[key] = add[key]
                    for key in delete.keys():
                        if key in next_state:
                            delete[key] = set([tuple(x) for x in delete[key]])  # translate from json format
                            next_state[key] = next_state[key].difference(delete[key])  # remove common predicates

                effect = self.search_state(next_state, goal, solved, closed, expended, depth - 1, timebound)
                if effect:  # effect is solved or loop or unknown
                    # continue to look at all effects of the action to decide if action is solved
                    if effect == 2:  # effect is a loop
                        loops += 1
                    elif effect == 3:  # unknown
                        if timebound - time.time() <= 0:  # timeout
                            if [x for x in solved if isinstance(x, list) and stateid in x]:  # stateid has solved action
                                solved.append(stateid)
                                return 1
                            return 3  # unknown
                        unknown += 1
                    i += 1
                    continue
                else:  # effect is closed->action is closed(check rest of actions)
                    i = -1
                    break

            # done looking at effects of action. decide if due to solved(finished) or closed(early)
            if i < 0 or i == loops:  # all effects are loops or a closed effect->add action to closed,check all actions to decide about state
                closed.append([stateid, action])
            #action has unknown effect(s),can't decide yet,check other actions to decide about state
            # are loops blocking from reaching goal
            elif unknown == 0 and i > 0:  # finished looking at all effects and no loops/unknown->action is solved->state also solved
                solved.append([stateid, action])  # check alternatives too
            else:  # not closed but had unknown effects->action is unknown->if state is not solved it is unknown!
                action_unknown = True

        if action_unknown:  # had unknown actions and state was not solved
            return 3
        if [x for x in solved if isinstance(x, list) and stateid in x]:  # action from stateid in solved
            solved.append(stateid)
            return 1
        closed.append(stateid)# looked at all actions and all were closed->state is closed
        return 0  # closed

    def update_model(self, current_state):
        expected = False  # flag to mark hidden predicates

        for index, state in enumerate(self.possible_states):
            if current_state == state:  # reached an expected state
                expected = True
        new_suspect = False  # flag to update file
        if not expected:  # hidden predicate was revealed/hidden(on top of an effect)
            # compare possible states and current_state
            revealed = set()
            hidden = set()
            mindiff = -1
            effect = None  # effect that happened without the hidden predicates
            for state in self.possible_states:
                statediff = set()
                add = {}
                delete = {}
                keys = list(set(itertools.chain.from_iterable([current_state.keys(), state.keys()])))
                for key in keys:
                    # find possible state closest to current-this must be the effect that happened->predicate hidden in the difference(minimal difference)
                    if key not in current_state:
                        diff = state[key]
                        tmp = list(state[key] - current_state[key])
                        if tmp:
                            delete[key] = tmp
                    elif key not in state:
                        diff = current_state[key]
                        tmp = list(current_state[key] - state[key])
                        if tmp:
                            add[key] = tmp
                    else:  # key in both
                        diff = current_state[key] ^ state[key]
                        tmp = list(current_state[key] - state[key])
                        if tmp:
                            add[key] = tmp
                        tmp = list(state[key] - current_state[key])
                        if tmp:
                            delete[key] = tmp
                    statediff = statediff.union(diff)

                    if 0 < mindiff < len(statediff):  # already found more similar state
                        break
                # done comparing states
                if mindiff < 0 or len(statediff) < mindiff:  # most similar state yet
                    mindiff = len(statediff)
                    revealed = add
                    hidden = delete
                    effect = state
            trigger = str(self.hash_state(effect))  # the expected effect
            if trigger not in self.suspect:
                new_suspect = True
                self.suspect[trigger] = [revealed, hidden]

        if new_suspect:  # new hidden predicate info
            task_file = open(self.task_path, 'w')
            self.closed = []  # reset closed since from now would be more reliable
            task_file.write(json.dumps({"suspect": self.suspect, "solved": self.solved, "closed": self.closed}))
            task_file.close()

    def hash_state(self, state):
        return hash(''.join(sorted(self.services.parser.predicates_from_state(state))))

    def get_successor_state(self, state, a, index):  # get i'th effect caused by action a
        # apply effects of action to state
        action_name, param_names = self.services.parser.parse_action(a)
        action = self.services.parser.actions[action_name]
        params = map(self.services.parser.get_object, param_names)
        param_mapping = action.get_param_mapping(params)

        if isinstance(action, Action):  #deterministic
            if index > 0:  # only one effect possible
                return None
            state_ = copy.deepcopy(state)
            for (predicate_name, entry) in action.to_delete(param_mapping):
                predicate_set = state_[predicate_name]
                if entry in predicate_set:
                    predicate_set.remove(entry)
            for (predicate_name, entry) in action.to_add(param_mapping):
                state_[predicate_name].add(entry)
            return copy.deepcopy(state_)
        else:  # nondeterministic action
            if index in range(len(action.addlists)):
                state_ = copy.deepcopy(state)
                for (predicate_name, entry) in action.to_delete(param_mapping, index):
                    predicate_set = state_[predicate_name]
                    if entry in predicate_set:
                        predicate_set.remove(entry)
                for (predicate_name, entry) in action.to_add(param_mapping, index):
                    state_[predicate_name].add(entry)
                return copy.deepcopy(state_)
        return None

    def count_subgoals(self, state, goal):
        count = 0
        for sub in goal.parts:
            count += self.services.parser.test_condition(sub, state)
        return count

    def get_uncomplete_subgoals(self, state, goal):
        subs = []
        for sub in goal.parts:
            if not self.services.parser.test_condition(sub, state):
                subs.append(sub)
        return subs

    def get_successor_states(self, state, a):
        # apply effects of action to state
        action_name, param_names = self.services.parser.parse_action(a)
        states = []
        action = self.services.parser.actions[action_name]
        params = map(self.services.parser.get_object, param_names)
        param_mapping = action.get_param_mapping(params)

        if isinstance(action, Action): # deterministic
            state_ = copy.deepcopy(state)
            for (predicate_name, entry) in action.to_delete(param_mapping):
                predicate_set = state_[predicate_name]
                if entry in predicate_set:
                    predicate_set.remove(entry)
            for (predicate_name, entry) in action.to_add(param_mapping):
                state_[predicate_name].add(entry)
            states.append(copy.deepcopy(state_))
        else:  # nondeterministic
            for index in range(len(action.addlists)):
                state_ = copy.deepcopy(state)
                for (predicate_name, entry) in action.to_delete(param_mapping, index):
                    predicate_set = state_[predicate_name]
                    if entry in predicate_set:
                        predicate_set.remove(entry)
                for (predicate_name, entry) in action.to_add(param_mapping, index):
                    state_[predicate_name].add(entry)
                states.append(copy.deepcopy(state_))
        return states


if input_flag == "-L":
    while True:
        print LocalSimulator().run(domain, problem, ImprovingExecutor())
elif input_flag == "-E":
    print LocalSimulator().run(domain, problem, ImprovingExecutor())

