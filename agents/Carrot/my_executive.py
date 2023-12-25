import json
import math
import os
import os.path
import random
import sys
from argparse import Namespace
from collections import OrderedDict

import pddlsim.planner as planner
from pddlsim.executors.executor import Executor
from pddlsim.local_simulator import LocalSimulator
# these two are needed for apply_action_to_state_delrelax
from pddlsim.parser_independent import Action, ProbabilisticAction

INFINITY = 100000
 # got this from the valid actions implementation in the repo
def get_valid_actions(services, state): 
    possible_actions = []
    for (name, action) in services.parser.actions.items():
        for candidate in get_valid_candidates_for_action(state, action):
            possible_actions.append(action.action_string(candidate))
    return possible_actions

def join_candidates(previous_candidates, new_candidates, p_indexes, n_indexes):
    shared_indexes = p_indexes.intersection(n_indexes)
    if previous_candidates is None:
        return new_candidates
    result = []
    for c1 in previous_candidates:
        for c2 in new_candidates:
            if all([c1[idx] == c2[idx] for idx in shared_indexes]):
                merged = c1[:]
                for idx in n_indexes:
                    merged[idx] = c2[idx]
                result.append(merged)
    return result

# NOTE: AFAIK this is a fix from the previous version of this, which can have issues when a parameter is unconstrained
def indexed_candidate_to_dicts(candidate, index_to_name, objects):
    candidates = [{name[0]: candidate[idx] for idx, name in index_to_name.items()}]
    done = False

    while not done:
        done = True

        for candidate in candidates:
            for name, value in candidate.items():
                if not value:
                    done = False

                    for obj in objects:
                        copy = dict(candidate)
                        copy[name] = obj

                        candidates.append(copy)

                        try:
                            candidates.remove(candidate)
                        except ValueError:
                            pass

    return candidates

def get_valid_candidates_for_action(state, action):
    """
    Get all the valid parameters for a given action for the current state of the simulation
    """
    signatures_to_match = {name: (idx, t) for idx, (name, t) in enumerate(action.signature)}
    index_to_name = {idx: name for idx, name in enumerate(action.signature)}
    candidate_length = len(signatures_to_match)
    found = set()
    candidates = None
    # copy all preconditions
    for precondition in sorted(action.precondition, key=lambda x: len(state[x.name])):
        thruths = state[precondition.name]
        if len(thruths) == 0:
            return []
        # map from predicate index to candidate index
        reverse_map = {idx: signatures_to_match[pred][0] for idx, pred in enumerate(precondition.signature)}
        indexes = reverse_map.values()
        precondition_candidates = []
        for entry in thruths:
            candidate = [None] * candidate_length
            for idx, param in enumerate(entry):
                candidate[reverse_map[idx]] = param
            precondition_candidates.append(candidate)

        candidates = join_candidates(candidates, precondition_candidates, found, indexes)
        # print( candidates)
        found = found.union(indexes)

    return [
        item
        for sublist in [
            indexed_candidate_to_dicts(c, index_to_name, [grounding[0] for grounding in state["="]])
            for c in candidates
        ]
        for item in sublist
    ]


def convert_action_to_name(action):
    return action[1:].split()[0]

def Is_NonDeterministic_problem(services):
    if len(services.parser.task.failure_probabilities) > 0:
        return True
    for action in services.parser.task.actions:
        if action.effects_probs is not None and len(action.effects_probs) > 1:
            return True
    return False

"""
When we are searching with the heuristic, we don't want to use the parsers implementation because 
I do not want to pick a random action. I want to pick the action with the highest probability like it was 
a determinisitc problem.
"""
def apply_action_to_state_ground_probabilites(services, action_sig):
    action_name, param_names = services.parser.parse_action(action_sig)
    action = services.parser.actions[action_name]
    params = map(services.parser.get_object, param_names)
    state_results = []
    param_mapping = action.get_param_mapping(params)

    if isinstance(action, Action):
        current_state = services.parser.copy_state(services.perception.get_state())
        for (predicate_name, entry) in action.to_delete(param_mapping):
            predicate_set = current_state[predicate_name]
            if entry in predicate_set:
                predicate_set.remove(entry)

        for (predicate_name, entry) in action.to_add(param_mapping):
            current_state[predicate_name].add(entry)
        state_results.append((current_state, 1))
    else:
        assert isinstance(action, ProbabilisticAction)
        # Use this when looking ahead in search, look ahead to the most probable future.
        #index = action.prob_list.index(max(action.prob_list))
        #index = action.choose_random_effect()
        for index in range(len(action.prob_list)):                
            current_state = services.parser.copy_state(services.perception.get_state())
            for (predicate_name, entry) in action.to_delete(param_mapping, index):
                predicate_set = current_state[predicate_name]
                if entry in predicate_set:
                    predicate_set.remove(entry)

            for (predicate_name, entry) in action.to_add(param_mapping, index):
                current_state[predicate_name].add(entry)
            state_results.append((current_state, action.prob_list[index]))
    
    return state_results

# modified from parser_independent.py in the pddlsim repository.
# self from repo is services.parser in here
# apply the actions without applying the delete list.
def apply_action_to_state_delrelax(services, action_sig, state):
    param_mapping, action = get_param_mapping(services, action_sig)
    #predicates_added_count = 0
    if isinstance(action, Action):
        for (predicate_name, entry) in action.to_add(param_mapping):
            if entry not in state[predicate_name]:
                state[predicate_name].add(entry)
                #predicates_added_count += 1
    else:
        assert isinstance(action, ProbabilisticAction)
        #index = action.prob_list.index(max(action.prob_list))
        for index in range(len(action.prob_list)):
        #index = random.randint(0,len(action.prob_list) - 1)
        #index = action.choose_random_effect()
            for (predicate_name, entry) in action.to_add(param_mapping, index):
                if entry not in state[predicate_name]:
                    state[predicate_name].add(entry)
                    #predicates_added_count += 1
    #return predicates_added_count

def apply_action_to_goal_ff(services, action_sig, goal):
    param_mapping, action = get_param_mapping(services, action_sig)
    #predicates_added_count = 0
    if isinstance(action, Action):
        for (predicate_name, entry) in action.to_add(param_mapping):
            if predicate_name in goal and entry in goal[predicate_name]:
                goal[predicate_name].remove(entry)
                preconditions = []
                for pre_predicate in action.precondition:
                    grounded = pre_predicate.ground(param_mapping)
                    if pre_predicate.name not in goal:
                        goal[pre_predicate.name] = set()
                    goal[pre_predicate.name].add(grounded)

            #if entry not in goal[predicate_name]:
            #    goal[predicate_name].add(entry)
            #    predicates_added_count += 1
    else:
        assert isinstance(action, ProbabilisticAction)
        #index = action.prob_list.index(max(action.prob_list))
        #index = random.randint(0,len(action.prob_list)-1)
        for index in range(len(action.prob_list)):
        #index = action.choose_random_effect()
            for (predicate_name, entry) in action.to_add(param_mapping, index):
                if predicate_name in goal and entry in goal[predicate_name]:
                        goal[predicate_name].remove(entry)
                        preconditions = []
                        for pre_predicate in action.precondition:
                            grounded = pre_predicate.ground(param_mapping)
                            if pre_predicate.name not in goal:
                                goal[pre_predicate.name] = set()
                            goal[pre_predicate.name].add(grounded)
    #return predicates_added_count

def get_param_mapping(services, action_sig):
    action_name, param_names = services.parser.parse_action(action_sig)
    action = services.parser.actions[action_name]
    params = map(services.parser.get_object, param_names)
    param_mapping = action.get_param_mapping(params)
    return param_mapping, action

def apply_actions(services, actions, state):
    #total = 0
    for action in actions:
        apply_action_to_state_delrelax(services, action, state)
        if goal_satisfied(services, state):
            #return total
            return
    #return total

def goal_satisfied(services, state):
    satisfied = 0
    if len(services.goal_tracking.uncompleted_goals) == 0:
        return True
    for sub_goal in services.goal_tracking.uncompleted_goals[0].parts:
        if services.parser.test_condition(sub_goal, state):
            satisfied += 1
    return len(services.goal_tracking.uncompleted_goals[0].parts) == satisfied

"""
This is used to check how much of the goal the action satisfies.
If more of the precondition of the action that leads to the goal are satisfied, 
the closer we are to the goal!
Unfortunetly, the idea is nice but the implementations is not good enough
so this was abandond in the end.
"""
def satisfies(action_obj, goal, list_name, state, services):
    satisfies = 0
    count = 0
    for add_predicate in getattr(action_obj, list_name):
        if add_predicate and add_predicate[0] == goal.predicate:
            temp = action_obj.get_param_mapping(state)
            for precondition in action_obj.precondition:
                count += 1
                param_mapping = {}
                for key, value in zip(add_predicate[1], goal.args):
                    if key in precondition.signature:
                        param_mapping[key] = value
                
                if len(param_mapping) == len(precondition.signature) and precondition.test(param_mapping, state):
                    satisfies += 1
    return satisfies, count

"""
This is a trick that tries to bipass hidden predicates.
The Idea is to use the precondition and action that leads to the goal to see how much of it 
we can solve using the current state we are in.
This does not work well anough, as the calculation is compilcated, the logic is hard and I didn't 
have anough time to try and make this really work.
"""
def Calculate_partly_score(services, score, state):
    precondition_list = []
    satisfies_total = 0
    count_total = 0
    for sub_goal in services.goal_tracking.uncompleted_goals[0].parts:
        for action_name, action_obj in services.parser.actions.items():
            if isinstance(action_obj, Action):
                list_name = "addlist"
            elif isinstance(action_obj, ProbabilisticAction): # has addlists instead of addlist
                list_name = "addlists"
            else:
                print "Bad pddl action, not Action or ProbabilisticAction"

            # check how much the action satisfies the sub goals preconditions.
            trus, count = satisfies(action_obj, sub_goal, list_name, state, services)
            satisfies_total += trus
            count_total += count
    #return score * (satisfies_total / count_total)
    """
    lower score is better. so as there are more satisfied predicates, the ratio will be closer to 1.
    else, the ratio will always be bigger from 1 hench the total score will be bigger.
    """
    if satisfies_total == 0:
        satisfies_total = 0.8 # stabelize numerical infinity
    return score * (count_total / satisfies_total) 

def Cheat(services, state):
    if not hasattr(services.parser, "revealable_predicates"):
        return state
    for element in services.parser.revealable_predicates:
        for effect in element.effects:
            state[effect[0]].add(effect[1])
    return state

# NOTE: This code is absolutely wrong, as some goals cannot be turned into
# states. However, this code is very much intentional and changing it would
# involve changing too much of the agent's architecture, and so naught will be
# done.
def convert_goal_to_state(services):
    result = {}
    for sub_goal in services.goal_tracking.uncompleted_goals[0].parts:
        if sub_goal.predicate not in result:
            result[sub_goal.predicate] = set()
            result[sub_goal.predicate].add(sub_goal.args)
        else:
            result[sub_goal.predicate].add(sub_goal.args)
    return result

def is_subdict(small, big):
    for key, value in small.items():
        if key not in big:
            return False
        if not value.issubset(big[key]):
            return False
    return True

def get_actions_subset(actions, goal, services, state):
    actions_sub_set = []
    random.shuffle(actions)
    for action in actions:
        temp = services.parser.copy_state(state)
        apply_action_to_state_delrelax(services, action, state)
        if state != temp:
            actions_sub_set.append(action)
        if is_subdict(goal, state):
            return actions_sub_set

def update_goal(curr_goal, actions, services):
    for action in actions:
        apply_action_to_goal_ff(services, action, curr_goal)
    return curr_goal

"""
A note about this with q learning:
To use this with partial goals and q learning we have to flip the way the huristic works.
Usually, we want to take the value that has the lowest huristic value. This is the opposite from q learning.
We define a extra parameter, max_score. so that all the scores will be in the range [0, max_score]
if for example our score is 0, then we want to return max_score.
We also "remember" what was the maximal FF score achived.
then, we use the inverted ratio between the maximal FF score and the real score, 
to calculate the value between the returned score and the max_score. 
"""
"""
What this does:
Start by cheating and adding the hidden predicates into the state.
then use the fast forward, Hadd heuristic. Keep adding actions to the state using delete relaxation, 
and count the number of fluents added untill we reach the goal. 
This is the heuristic score we will use.
Also use caching to speed up search in large spaces.
"""
#FF_score_cach = {}
def Get_FF_score(services, InitialState):
    steps = 0
    ser = serialize_state(InitialState)
    Ak = []
    Sk = []
    #if ser in FF_score_cach:
    #    return FF_score_cach[ser]
    # cheat by calculating the hidden predicates into the heuristic.
    relaxed_state = Cheat(services, services.parser.copy_state(InitialState))
    while True:
        actions = get_valid_actions(services, relaxed_state)
        random.shuffle(actions)
        Ak.append(actions)
        relaxed_state_result = services.parser.copy_state(relaxed_state)
        apply_actions(services, actions, relaxed_state_result) # returnes the number of fluents added to the state
        if goal_satisfied(services, relaxed_state_result):
            #FF_score_cach[serialize_state(InitialState)] = total_fluents_added
            #return total_fluents_added
            break
        if relaxed_state_result == relaxed_state: # we reached the end, so just return the a really large number. can't solve the problem.
            # the next lines were used as a trick before the cheating was added. That didn't work well.
            #score = Calculate_partly_score(services, total_fluents_added, relaxed_state)
            #FF_score_cach[serialize_state(InitialState)] = score
            #return score
            return INFINITY
        else:
            relaxed_state = relaxed_state_result
        Sk.append(relaxed_state_result)
        steps += 1
    
    goal = convert_goal_to_state(services)
    relaxed_plan = []
    for i in range(steps, 0, -1):
        curr_actions = Ak[i]
        curr_state = Sk[i - 1] # if we pick Sk[i], i = steps - 1 obviusly it satisfied the goal.
        actions_sub_set = get_actions_subset(curr_actions, goal, services, curr_state)
        if actions_sub_set is None:
            continue
        relaxed_plan.append(actions_sub_set)
        goal = update_goal(goal, actions_sub_set, services)
    
    total = 0
    for step in relaxed_plan:
        total += len(step)
    #FF_score_cach[ser] = total
    return total
        
def Has_Hidden_Goals(services):
    if len(services.parser.revealable_predicates) > 0:
        return True
    return False

def remove_suffix(name):
    if name.endswith(".pddl"):
        return name[:-5]
    return name

# this is used to serialize the states into strings, use sorting to achevie this.
def serialize_state(state):
    output = OrderedDict()
    state_keys = list(state.keys())
    state_keys.sort()
    for key in state_keys:
        value = state[key]
        new_value = []
        for v in value:
            new_value.append(v)
        new_value.sort()
        output[key] = new_value
    return str(output)

"""pick uniformly randomly from the actions by the name.
       then pick uniformly randomly from the parameters"""
def pick_random_action(valid_actions):
        action_names_set = set()
        for action in valid_actions:
            action = convert_action_to_name(action)
            action_names_set.add(action)
        picked_name = random.choice(tuple(action_names_set))
        actions_by_name = [action for action in valid_actions if picked_name in action]
        return random.choice(actions_by_name)

# this is the base class of all the agents, holds general members that are relevant for all
class Agent(Executor):
    def __init__(self, domain, problem):
        self.domain = remove_suffix(domain)
        self.problem = remove_suffix(problem)
   
    def initialize(self, services):
        self.services = services
        self.IsNonDeterminitic = Is_NonDeterministic_problem(services)
        self.HasHiddenGoals = Has_Hidden_Goals(services)
        self.FileName = self.domain + "_" + self.problem + ".txt"
        self.IsLearned = os.path.exists(self.FileName)

"""
In my testing, learning didn't really improve anything and the learning time was a waste.
This is why this class just retuens exit(128) and does nothing.
I left the old code in comment, so that you could see what I did in testing.
"""
class MetaLearner(Agent):
    def __init__(self, domain, problem):
        super(MetaLearner, self).__init__(domain, problem)
        self.learner = None

    def initialize(self, services):
        super(MetaLearner, self).initialize(services)
        """
        if not self.IsNonDeterminitic:
            self.learner = DeterministicLearner(self.domain, self.problem)
        elif self.IsNonDeterminitic and not self.HasHiddenGoals:
            self.learner = HeuristicAgent(self.domain, self.problem)
        elif self.IsNonDeterminitic and self.HasHiddenGoals:
            self.learner = QlearningLearner(self.domain, self.problem)
        else:
            self.learner = DeterministicLearner(self.domain, self.problem)
        """
        #self.learner = QlearningLearner(self.domain, self.problem)
        #self.learner.initialize(services)
        self.learner = None # :)
    
    def next_action(self):
        
        #if self.learner is None:
        #    return None
        #return self.learner.next_action()
        
        exit(128)

class MetaExecutor(Agent):
    def __init__(self, domain, problem):
        super(MetaExecutor, self).__init__(domain, problem)
        self.executor = None

    def initialize(self, services):
        super(MetaExecutor, self).initialize(services)
        """
        This is the old logic for picking an agent:
        In practice, the heuristic search gives the best results overall.
        if not self.IsNonDeterminitic:
            self.executor = DeterministicExecutor(self.domain, self.problem)
        elif self.IsNonDeterminitic and not self.HasHiddenGoals:
            self.executor = HeuristicAgent(self.domain, self.problem)
        elif self.IsNonDeterminitic and self.HasHiddenGoals:
            self.executor = QlearningExecutor(self.domain, self.problem)
        else:
            self.executor = DeterministicExecutor(self.domain, self.problem)
            """
        if not self.IsNonDeterminitic:
            self.executor = DeterministicExecutor(self.domain, self.problem)
        else:
            self.executor = HeuristicAgent(self.domain, self.problem)
        self.executor.initialize(services)
    
    def next_action(self):
        if self.executor is None:
            return None
        return self.executor.next_action()

"""
This is a determinstic learner. It calculates the plan with the planner and saves it to a file.
This really didn't improve computing time so this was abandond.
"""
class DeterministicLearner(Agent):
    def __init__(self, domain, problem):
        super(DeterministicLearner, self).__init__(domain, problem)

    def initialize(self, services):
        super(DeterministicLearner, self).initialize(services)
        self.make_steps()

    def make_steps(self):
        self.steps = planner.make_plan(self.services.pddl.domain_path, self.services.pddl.problem_path)
        with open(self.FileName, "w") as steps:
            steps.write(json.dumps(self.steps))
    
    def next_action(self):
        exit(128)

"""
This is an agents that makes a plan and follows it to the goal.
Uses a fallback to a random agent if it gets to en unexcpected plan, 
altough that never happens because in probabillistic domains there is another
aganet.
"""
class DeterministicExecutor(Agent):
    def __init__(self, domain, problem):
        super(DeterministicExecutor, self).__init__(domain, problem)
        self.Fallback = False

    def initialize(self, services):
        super(DeterministicExecutor, self).initialize(services)
        self.init_steps()

    def next_action(self):
        actions = self.services.valid_actions.get()

        if self.services.goal_tracking.reached_all_goals() or len(actions) == 0:
            return None

        if self.Fallback:
            return self.Fallback_pick(actions)

        plan_pick = None
        if len(self.steps) > 0: # pick an action from the plan
            plan_pick = self.steps.pop(0).lower()

        # if there is no action in the plan or the plan dosn't fit the enviroment
        if plan_pick is None or plan_pick not in actions:
            self.Fallback = True # Fallback to a random agent.
        
        if self.Fallback:
            return pick_random_action(actions)

        return plan_pick

    def init_steps(self):
        try:
            with open(self.FileName, "r") as steps_file:
                data = steps_file.read()
                self.steps = json.loads(data)
        except EnvironmentError:
            self.steps = planner.make_plan(self.services.pddl.domain_path, self.services.pddl.problem_path)

"""
This is the super agent, the one that is the best one and that is used for the hard problems.
This agents uses a best-first-search approach with the heuristic that is calculated in the global
function. 
Because how the heuristic is built, this has kind of an iterative-deepening strategy.
"""
class HeuristicAgent(Agent):
    def __init__(self, domain, problem):
        super(HeuristicAgent, self).__init__(domain, problem)

    def initialize(self, services):
        super(HeuristicAgent, self).initialize(services)
        self.visited = set()
        self.last_action_str = ""
        self.last_state_ser = ""

    
    def pick_action_based_on_heuristic(self, actions):
        values = []
        states = []
        for action in actions:
            # for each action check the state it takes us to and calculate its heuristic value.
            init_state = self.services.parser.copy_state(self.services.perception.get_state())
            result_states = apply_action_to_state_ground_probabilites(self.services, action)
            states.append(init_state)
            score = 0
            for state, probability in result_states:
                h_score = Get_FF_score(self.services, state)
                if serialize_state(state) in self.visited:
                    h_score += 1
                score += probability * h_score
            #score = Get_FF_score(self.services, init_state) 
            values.append(score)
        min_val = min(values)
        index = values.index(min_val)
        if all(x == min_val for x in values): # if all the values are the same
            for i, state in enumerate(states): # remove the states and actions that we already visited in this level.
                if serialize_state(state) in self.visited:
                    del states[i]
                    del actions[i]
            return pick_random_action(actions), min_val, values
        if actions[index] == self.last_action_str:
            values.remove(min_val)
            del actions[index]
            min_val = min(values)
            index = values.index(min_val)
        return actions[index], min_val, values

    def next_action(self):
        curr_state = self.services.perception.get_state()
        actions = self.services.valid_actions.get()
        if self.services.goal_tracking.reached_all_goals() or len(actions) == 0:
            return None
        if len(actions) == 1:
            return actions[0]
        #if self.last_state_ser == serialize_state(self.services.perception.get_state()):
        #    return self.last_action_str
        picked, value, _ = self.pick_action_based_on_heuristic(actions)
        self.last_state_ser = serialize_state(self.services.perception.get_state())
        self.visited.add(self.last_state_ser )
        self.last_action_str = picked
        return picked

"""
From my testing, and because the way my heuristic is built this A* agent isn't better from the greedy one.
Because we do not see the whole graph structrue and we can pick only the nodes were our agent is. 
Because each action has the cost of 1.
Because out heuristic is built with levels.
F is usually the same for all neigbors, and we get a not usefull agent.
"""
class AstarAgent(DeterministicExecutor): # impelment A* for out agent
    def __init__(self, domain, problem):
        super(AstarAgent, self).__init__(domain, problem)

    def initialize(self, services):
        super(AstarAgent, self).initialize(services)
        self.visited = set()
        self.last_action = ""
        actions_num = len(services.parser.task.actions)
        max_nodes = 100
        # the tree search has ~ actions_num ^ (k + 1) nodes.
        self.k = int(math.ceil(math.log(max_nodes) / math.log(actions_num)))
        self.G_scores = {}
        self.F_scores = {}
        initial_state = self.services.perception.get_state()
        initial_state_ser = serialize_state(initial_state)
        self.G_scores[initial_state_ser] = 0
        self.F_scores[initial_state_ser] = Get_FF_score(services, initial_state)
        self.last_G_score = 0
 
    def next_action(self):
        actions = self.services.valid_actions.get() 
        # prevent agent from doing the same action forever.
        actions = [action for action in actions if not self.last_action == action] 
        random.shuffle(actions) # prevent non-sense action repeates.
        current_state = self.services.perception.get_state()
        current_state_ser = serialize_state(current_state)
        if current_state_ser not in self.G_scores:
            self.G_scores[current_state_ser] = self.last_G_score + 1
        self.visited.add(serialize_state(current_state))
        if self.services.goal_tracking.reached_all_goals() or len(actions) == 0:
            return None
        if len(actions) == 1:
            return actions[0]
        neighbor_states = []
        neighbor_Fscores = []
        for action in actions:
            neighbor = self.services.parser.copy_state(self.services.perception.get_state())
            self.services.parser.apply_action_to_state(action, neighbor, check_preconditions=False)
            neighbor_states.append(neighbor)
            neighbor_ser = serialize_state(neighbor)
            if neighbor_ser not in self.G_scores:
                self.G_scores[neighbor_ser] = INFINITY
            if neighbor_ser not in self.F_scores:
                self.F_scores[neighbor_ser] = INFINITY
            neighbor_h = Get_FF_score(self.services, neighbor)
            tentative_gScore = self.G_scores[current_state_ser] + 1 # the cost of each action is one. so d(x,y) = 1
            if tentative_gScore < self.G_scores[neighbor_ser]:
                self.G_scores[neighbor_ser] = tentative_gScore
                f = tentative_gScore + neighbor_h
                neighbor_Fscores.append(f)
                self.F_scores[neighbor_ser] = f
            else:
                neighbor_Fscores.append(self.F_scores[neighbor_ser])
        
        min_f_score = min(neighbor_Fscores)
        min_index = neighbor_Fscores.index(min_f_score)
        picked = actions[min_index]
        self.next_state_ser = serialize_state(neighbor_states[min_index])
        self.last_G_score = self.G_scores[current_state_ser]
        self.last_action = picked
        print "F score for picked action: " + str(min_f_score)
        return picked

"""
This is the base class for all agents that use q learning.
This holds some members and methods that are relevant both for the 
exceutor and the learner.
"""
class QAgent(Agent):
    def __init__(self, domain, problem):
        super(QAgent, self).__init__(domain, problem)
        self.GoalFinishedReward = 1000
        self.SubGoalFinishedReward = 0.5 * self.GoalFinishedReward
        self.HeurMaxReward = 0.5 * self.GoalFinishedReward
        self.max_heuristic_value = 0

    def initialize(self, services):
        super(QAgent, self).initialize(services)
        self.init_Qtable()

    def init_Qtable(self):
        try:
            with open(self.FileName, "r") as file:
                data = file.read()
                if len(data) == 0:
                    self.Qtable = {}
                    return
                self.Qtable = json.loads(data)
        except EnvironmentError:
            self.Qtable = {}
            return

    # calculate and return the action that has the biggest Q value.
    def calculate_Qmax_action(self, valid_actions, current_state): # get the state in it's unserialized form
        action_values = []
        for i, action in enumerate(valid_actions):
            action_values.append(self.get_Qtable_value(current_state, convert_action_to_name(action)))
        max_value = max(action_values)
        max_index = action_values.index(max_value)
        if all(x > max_value - 0.001 and x < max_value + 0.001 for x in action_values): # check that we have a true max
            return pick_random_action(valid_actions), 0
        return valid_actions[max_index], max_value

    # based on: https://stats.stackexchange.com/questions/252455/normalization-when-max-and-min-values-are-reversed
    def do_score_conversion(self, score):
        normalized = (self.max_heuristic_value - score) / self.HeurMaxReward
        return normalized

    # return a Q value of a state and action pair.
    def get_Qtable_value(self, state, action_name): # get the state in it's unserialized form
        state_serialzied = serialize_state(state)
        if state_serialzied in self.Qtable:
            if action_name in self.Qtable[state_serialzied]:
                return self.Qtable[state_serialzied][action_name]
        # state not in qtable. initialize it with heuristic value instead of 0.
        hscore = self.get_state_hscore(state)
        self.add_pair_to_qtable(state_serialzied, action_name, hscore)
        return hscore
    
    # get the heuristic score of a state normalized for q learning.
    def get_state_hscore(self, state):
        score = Get_FF_score(self.services, state)
        if score > self.max_heuristic_value:
            self.max_heuristic_value = score
        score = self.do_score_conversion(score)
        return score

    def add_pair_to_qtable(self, state, action, value): # the state should be serialized
        if state not in self.Qtable:
            self.Qtable[state] = {}
        self.Qtable[state][action] = value

"""
This is the agent that is activated in the q learning phase. Its goal is to generate a good q table
that the excetor coult use. It uses potential q learning, and each cell in the table is initialized
with the value of the heuristic for that state.
"""
class QlearningLearner(QAgent): 
    def __init__(self, domain, problem):
        super(QlearningLearner, self).__init__(domain, problem)
        self.epsilon = -1
        self.alpha = 0.001
        self.gamma = 0.9

    def initialize(self, services):
        super(QlearningLearner, self).initialize(services)
        self.last_action = ""
        self.last_state_ser = ""
        self.last_state_non_ser = ""
        self.last_uncompleted_goal_length = 0
        self.visited = set()

    def next_action(self):
        actions = self.services.valid_actions.get()
        if self.services.goal_tracking.reached_all_goals() or len(actions) == 0:
            self.update_qtable(0, self.GoalFinishedReward)
            return None

        picked_action, action_value = self.choose_apsilon_greedy(actions, self.services.perception.get_state())

        if self.last_action == "" and self.last_state_ser == "":
            return self.on_exit(picked_action)
        self.visited.add(self.last_state_ser)
        self.update_qtable(action_value, self.get_reward(self.last_action, self.last_state_non_ser))
        return self.on_exit(picked_action)

    def on_exit(self, picked_action):
        self.last_action = picked_action
        self.last_state_ser = serialize_state(self.services.perception.get_state())
        self.last_state_non_ser = self.services.parser.copy_state(self.services.perception.get_state())
        return picked_action

    # the problem is that H values are saves in Q table, then going around and around in these values that are getting updated.
    # this is the update step of the q learning algorithm
    def update_qtable(self, action_value, reward):
        last_action_name = convert_action_to_name(self.last_action)
        old_value = self.get_Qtable_value(self.last_state_non_ser, last_action_name)
        new_value = (1 - self.alpha) * old_value + self.alpha * (reward +  self.gamma * action_value)
        self.add_pair_to_qtable(self.last_state_ser, last_action_name, new_value)
        self.write_Qtable()

    # use epsilon greedy method to determin between exploration and exploitation.
    def choose_apsilon_greedy(self, valid_actions, current_state): # get the state unserialized
        if random.uniform(0, 1) < self.epsilon:
            action = pick_random_action(valid_actions) # Explore action space
            return action, self.get_Qtable_value(current_state, convert_action_to_name(action))
        else:
            max_action, max_value = self.calculate_Qmax_action(valid_actions, current_state) # Exploit learned values
            return max_action, max_value
            
    def write_Qtable(self):
        with open(self.FileName, "w") as file:
            to_json = json.dumps(self.Qtable)
            file.write(to_json)

    # the reward is just for getting to the goals, this is because we are solving a general problem.
    def get_reward(self, action, state):
        completed_goals = 0
        for sub_goal in self.services.goal_tracking.uncompleted_goals[0].parts:
            if self.services.parser.test_condition(sub_goal, state):
                completed_goals += 1
        score = completed_goals - self.last_uncompleted_goal_length
        self.last_uncompleted_goal_length = completed_goals
        if score != 0:
            return score * self.SubGoalFinishedReward
        return score

"""
This agent executes the previous q learning agents policy. The agents just goes 
from the start and picks the next action by picking the highest value from the 
q table.
"""
class QlearningExecutor(QAgent):
    def __init__(self, domain, problem):
        super(QlearningExecutor, self).__init__(domain, problem)
    
    def initialize(self, services):
        super(QlearningExecutor, self).initialize(services)

    def next_action(self):
        actions = self.services.valid_actions.get()
        if self.services.goal_tracking.reached_all_goals() or len(actions) == 0:
            return None
        
        max_action, _ = self.calculate_Qmax_action(actions, self.services.perception.get_state())
        return max_action

"""
The next 3 function were used to try generate a deterministic domain from a probablistic one.
This is not used in the final solution.
"""
def find_parens(s): # return the dict and the end index
    toret = {}
    pstack = []

    for i, c in enumerate(s):
        if c == '(':
            pstack.append(i)
        elif c == ')':
            if len(pstack) == 0:
                return toret, i
            toret[pstack.pop()] = i

    if len(pstack) > 0:
        raise IndexError("No matching opening parens at: " + str(pstack.pop()))

    return toret, len(s)

def get_second_distnace_parens(paren_dict):
    first = (0, 0)
    for key, value in paren_dict.items():
        if value - key > first[1] - first[0]:
            first = (key, value)
    del paren_dict[first[0]]
    second = (0, 0)
    for key, value in paren_dict.items():
        if value - key > second[1] - second[0]:
            second = (key, value)
    return second

def pre_procces_domain_file(domain_name):
    outfile = open("preprocced_" + domain_name, "w")
    inFile = open(domain_name, "r")
    output_data = []
    in_data = inFile.readlines()
    i = 0
    while i <len(in_data):
        line = in_data[i]
        if ":effect" in line:
            output_data.append(line)
            effect_str = ""
            j = i
            while ":action" not in line: # make line to be all the effects
                j += 1
                if j >= len(in_data) or ":action" in in_data[j]:
                    break
                effect_str += in_data[j]
            if j < len(in_data):
                i += j - i - 2
            suffix = effect_str[effect_str.rindex(")"):]
            effect_str = effect_str[:effect_str.rindex(")")]
            parents_dict, index = find_parens(effect_str)
            if index < len(effect_str):
                suffix += effect_str[index:]
            second_size = get_second_distnace_parens(parents_dict)
            effect_str = effect_str[second_size[0]:second_size[1]]
            output_data.append(effect_str + suffix)
        else:
            output_data.append(line)
        i += 1
    for line in output_data:
        outfile.write(line)

def main():
    mode_flag = sys.argv[1]
    domain = sys.argv[2]
    problem = sys.argv[3]
    
    if mode_flag == "-L":
        print LocalSimulator().run(domain, problem, MetaLearner(domain, problem))
    elif mode_flag == "-E":
        print LocalSimulator().run(domain, problem, MetaExecutor(domain, problem))
    else:
        print "Bad mode flag!"


if __name__ == "__main__":
    main()
