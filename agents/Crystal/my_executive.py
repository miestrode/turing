# general imports
import sys
import random
import os
import json

# the next line that is commented is only needed on my machine 
#sys.path.append("/usr/local/lib/python2.7/dist-packages")

# simulator related imports
from pddlsim.local_simulator import LocalSimulator
from pddlsim.executors.executor import Executor
from pddlsim.fd_parser import ProbabilisticAction
from pddlsim.fd_parser import Action
import pddlsim.planner as planner

# read files
input_flag = sys.argv[1]
domain_path = sys.argv[2]
problem_path = sys.argv[3]

# parse the input flag
if input_flag == '-L': 
    execution_phase = False
elif input_flag == '-E': 
    execution_phase = True
else: 
    raise NameError('Wrong input flag')

# executor implementation
class PRE_Executor(Executor):
    """ PRE_Executor - operates using 3 main operational modes:
        1. Plan dispatch like mode, which receives a plan and tries to follow it.
        2. React mode, which handles the case of deviation from the plan.
        3. Explore mode, which is invoked when no plan is found.
    """
    def __init__(self):
        super(PRE_Executor, self).__init__()
        self.deterministic_plan_dispatch = False
        self.probabilistic_plan_dispatch = False
        self.react = False
        self.explore = False
        self.pure_random = True
        self.exit_immediately = False
        self.prev_action = None
        self.prev_state = None
        self.curr_state = None
        self.expected_state = None
        self.deterministic_actions = None
        self.prev_num_predicates = 0
        self.curr_num_predicates = 0
        self.revealed_predicates = {}
        self.plan = []
        
    def initialize(self, services):
        self.services = services
        self.parse_domain_and_problem_names()
        self.curr_state = self.services.perception.get_state()
        self.prev_num_predicates = self.count_predicates(self.curr_state)
        self.initialize_revealed_predicates()
        self.expected_state = self.curr_state
        self.check_if_deterministic_domain()
        if self.is_deterministic_domain:
            file_path = self.full_name + "-plan"
            # if plan doesn't exists then generate it and save to file
            if not os.path.isfile(file_path):
                self.plan = planner.make_plan(self.services.pddl.domain_path,
                                              self.services.pddl.problem_path)
                with open(file_path, 'w') as json_file:
                    json.dump(self.plan, json_file, indent=4)
                    
            if not execution_phase: # this is the learning phase
                exit(128)
                
            else: # this is indeed the execution phase
                self.deterministic_plan_dispatch = True
                if len(self.plan) == 0: # need to load plan from file
                    with open(file_path) as f:
                        self.plan = json.load(f)
                        
        else: # self.is_deterministic_domain == False
            # check if env has already been explored
            file_path = self.domain + "-" + self.env + "-revealed_predicates"
            if not os.path.isfile(file_path):
                # try to find a plan, maybe no exploration is needed
                # derive the deterministic actions and save to file
                self.deterministify()
                domain_file_path = self.domain + '-deterministic_version.pddl'
                self.generate_domain(domain_file_path, self.deterministic_actions)
                # generate the tmp problem file and save to file
                problem_file_path = self.full_name + "-tmp_problem.pddl"
                self.services.parser.generate_problem(
                    problem_file_path, self.curr_state, self.services.parser.goals[0])
                # generate plan
                self.plan = planner.make_plan(domain_file_path, problem_file_path)
                if len(self.plan) == 0: # no plan was found
                    # need to explore
                    self.explore = True
                    
                else: # no need to explore
                    if not execution_phase: # this is the learning phase
                        exit(128)
                        
                    else: # this is indeed the execution phase
                        self.probabilistic_plan_dispatch = True
                
            else: # no need to explore
                if not execution_phase: # this is the learning phase
                    # we finished learning so exit immediately
                    self.exit_immediately = True
                    
                else: # this is indeed the execution phase
                    self.probabilistic_plan_dispatch = True
                    # derive the deterministic actions and save to file
                    self.deterministify()
                    domain_file_path = self.domain + '-deterministic_version.pddl'
                    self.generate_domain(domain_file_path, self.deterministic_actions)
                    # generate the tmp problem file and save to file
                    problem_file_path = self.full_name + "-tmp_problem.pddl"
                    self.services.parser.generate_problem(
                        problem_file_path, self.curr_state, self.services.parser.goals[0])
                    # generate plan
                    self.plan = planner.make_plan(domain_file_path, problem_file_path)
        
    def next_action(self):
        """ Main control loop.
        """
        ### debug
        # return None
        ### debug done
        
        if self.exit_immediately:
            print 'Agent PRE does not need more learning time, exiting'
            return None
        
        if self.deterministic_plan_dispatch: 
            return self.deterministic_plan_dispatch_mode()
        
        if self.probabilistic_plan_dispatch: 
            return self.probabilistic_plan_dispatch_mode()
        
        if self.react: 
            return self.react_mode()
        
        if self.explore:
            return self.explore_mode()

    ### operation modes:
    def deterministic_plan_dispatch_mode(self):
        if len(self.plan) > 0:
            return self.plan.pop(0).lower()
        
        return None
    
    def probabilistic_plan_dispatch_mode(self):
        if self.services.goal_tracking.reached_all_goals():
            return None
        
        # perceive state and check if the last action acheived the desired effect
        self.curr_state = self.services.perception.get_state()
        self.add_knowledge_revealed()
        if self.curr_state != self.expected_state:
            if self.curr_state != self.prev_state:                
                self.probabilistic_plan_dispatch = False
                self.react = True
                return self.react_mode()
            
            else: # self.curr_state == self.prev_state
                return self.prev_action
        
        if len(self.plan) > 0:
            deterministic_action = self.plan.pop(0).lower()
            chosen_action = self.choose_probabilistic_action(deterministic_action)
            self.update_documentation(chosen_action, deterministic_action)
            
        else: # len(self.plan) == 0
            deterministic_action = None
            print 'fatal error: no steps left in plan, but goal was not reached'
            chosen_action = None
        
        return chosen_action
    
    def react_mode(self):
        # find a new plan
        domain_file_path = self.domain + '-deterministic_version.pddl'
        self.generate_domain(domain_file_path, self.deterministic_actions)
        problem_file_path = self.full_name + "-tmp_problem.pddl"
        self.services.parser.generate_problem(
            problem_file_path, self.curr_state, self.services.parser.goals[0])
        self.plan = []
        self.plan = planner.make_plan(domain_file_path, problem_file_path) 
        if len(self.plan) > 0: # plan found!
            self.react = False
            self.probabilistic_plan_dispatch = True
            self.expected_state = self.curr_state
            return self.probabilistic_plan_dispatch_mode()
        
        else:
            print 'fatal error: plan not found in react mode'
            return None
        
    
    def explore_mode(self):
        # perceive state and check if predicates were revealed
        self.curr_state = self.services.perception.get_state()
        self.add_knowledge_revealed()
        self.curr_num_predicates = self.count_predicates(self.curr_state)
        if self.curr_num_predicates > self.prev_num_predicates:
            revealed_predicates = self.get_revealed_predicates()
            self.update_revealed_predicates(revealed_predicates)
            file_path = self.domain + "-" + self.env + "-revealed_predicates"
            dict_to_save = self.encode_for_jason(self.revealed_predicates)
            with open(file_path, 'w') as json_file:
                    json.dump(dict_to_save, json_file, indent=4)
            
            # try to find a new plan
            domain_file_path = self.domain + '-deterministic_version.pddl'
            self.generate_domain(domain_file_path, self.deterministic_actions)
            problem_file_path = self.full_name + "-tmp_problem.pddl"
            self.services.parser.generate_problem(
                problem_file_path, self.curr_state, self.services.parser.goals[0])
            self.plan = []
            self.plan = planner.make_plan(domain_file_path, problem_file_path) 
            if len(self.plan) > 0: # plan found!
                if not execution_phase: # this is the learning phase
                    # we finished learning so exit immediately
                    return None
                    
                self.explore = False
                self.probabilistic_plan_dispatch = True
                self.expected_state = self.curr_state
                return self.probabilistic_plan_dispatch_mode()
        
        # either no predicates were revealed or no plan was found: keep exploring
        if self.pure_random: # simple random agent
            if self.services.goal_tracking.reached_all_goals():
                chosen_action = None
                
            else:
                options = self.services.valid_actions.get()
                if len(options) == 0: 
                    chosen_action = None
                    
                elif len(options) == 1: 
                    chosen_action = options[0]
                    
                else:
                    chosen_action = random.choice(options)
                    
        # else: # random agent with soft avoid the past 
        
        self.update_documentation(chosen_action)
        return chosen_action
    
    ### supporting routines:
    def parse_domain_and_problem_names(self):
        """ Extract domain from domain name,
        env and task from the problem name, which is encoded as <env>-<task>.
        """
        self.domain = self.services.parser.task.domain_name
        self.problem = self.services.parser.task.task_name
        self.env, self.task = self.problem.split('-')
        self.full_name = self.domain + "-" + self.problem
    
    def check_if_deterministic_domain(self):
        self.is_deterministic_domain = True
        for (name, action) in self.services.parser.actions.items():
            if isinstance(action, ProbabilisticAction):       
                self.is_deterministic_domain = False
                break
    
    def deterministify(self):     
        """ Takes a mixed set of probabilistic and deterministic actions
        and converts them to a set of deterministic actions, according
        to pre-specified rules.
        """
        new_actions = {}
        for (name, action) in self.services.parser.actions.items():
            if isinstance(action, Action):
                new_actions[name] = action
            else: # isinstance(action, ProbabilisticAction) == True
                for i in range(len(action.prob_list)):
                    if len(action.addlists[i]) > 0:
                        new_name = name + str(i)
                        addlist = action.addlists[i]
                        dellist = action.dellists[i]
                        new_action = Action(new_name, action.signature, addlist, 
                                            dellist, action.precondition)
                        new_actions[new_name] = new_action
        
        # merge duplicate actions
        key_list = new_actions.keys()
        action_list = new_actions.values()
        to_delete_list = []
        if len(action_list) > 1:
            for i in range(len(action_list) - 1):
                for j in range(i + 1, len(action_list)):
                    if self.is_same_action(action_list[i], action_list[j]):
                        to_delete_list.append(i)
                        break
        
        for i in to_delete_list:
            key = key_list[i]
            del new_actions[key]
            
        self.deterministic_actions = new_actions
    
    def is_same_action(self, action1, action2):
        """ Takes two deterministic actions and checks if they
        are identical up to a different naming of parameters.
        """
        answer = False
        precondition1_dict = {}
        for predicate in action1.precondition:
            precondition1_dict[predicate.name] = []
        
        for predicate in action1.precondition:
            precondition1_dict[predicate.name].append(predicate)
        
        precondition2_dict = {}
        for predicate in action2.precondition:
            precondition2_dict[predicate.name] = []
        
        for predicate in action2.precondition:
            precondition2_dict[predicate.name].append(predicate)
        
        # basic test: same predicate names and same number of predicates
        if sorted(precondition1_dict.keys()) != sorted(precondition2_dict.keys()):
            return answer
        
        for (name, predicate_list) in precondition1_dict.items():
            if len(predicate_list) != len(precondition2_dict[name]):
                return answer
            
            num_negated1 = 0
            num_negated2 = 0
            for predicate in predicate_list:
                if predicate.negated:
                    num_negated1 += 1
                    
            for predicate in precondition2_dict[name]:
                if predicate.negated:
                    num_negated2 += 1
                    
            if num_negated1 != num_negated2:
                return answer
                
        # first try to find a mapping
        param_mapping = {}
        for (name, predicate_list) in precondition1_dict.items():
            if len(predicate_list) == 1:
                predicate1 = predicate_list[0]
                predicate2 = precondition2_dict[name][0]
                if predicate1.signature != predicate2.signature:
                    for i in range(len(predicate1.signature)):
                        param1 = predicate1.signature[i]
                        param2 = predicate2.signature[i]
                        if param1 != param2:
                            param_mapping[param1] = param2
        
        # apply the mapping to precondition and check if identical
        for (name, predicate_list) in precondition1_dict.items():
            for i in range(len(predicate_list)):
                predicate1 = predicate_list[i]
                found_predicate_mapping = False
                predicate_mapping = -1 # default non-valid value
                for j in range(len(predicate1.signature)):
                    param1 = predicate1.signature[j]
                    if param1 in param_mapping.keys():
                        param1 = param_mapping[param1]
                    
                    if len(predicate_list) == 1:
                        predicate2 = precondition2_dict[name][i]
                        param2 = predicate2.signature[j]
                        if param1 != param2:
                            return answer
                        
                    elif not found_predicate_mapping: # len(predicate_list) > 1
                        for k in range(len(precondition2_dict[name])):
                            predicate2 = precondition2_dict[name][k]
                            param2 = predicate2.signature[j]
                            if param1 == param2:
                                found_predicate_mapping = True
                                predicate_mapping = k
                                break
                                
                        if not found_predicate_mapping:
                            return answer
                        
                    else: # len(predicate_list) > 1 and found_predicate_mapping == True
                        predicate2 = precondition2_dict[name][predicate_mapping]
                        param2 = predicate2.signature[j]
                        if param1 != param2:
                            return answer
        
        # apply the mapping to addlist and check if identical
        sorted_addlist1 = sorted(action1.addlist)
        sorted_addlist2 = sorted(action2.addlist)
        if not self.is_same_effect_list(sorted_addlist1, sorted_addlist2, param_mapping):
            return answer
            
        # apply the mapping to deldlist and check if identical
        sorted_dellist1 = sorted(action1.dellist)
        sorted_dellist2 = sorted(action2.dellist)
        if not self.is_same_effect_list(sorted_dellist1, sorted_dellist2, param_mapping):
            return answer
        
        answer = True
        return answer
    
    def is_same_effect_list(self, effect_list1, effect_list2, 
                            param_mapping1, param_mapping2 = {}):
        answer = False
        if len(effect_list1) != len(effect_list2):
            return answer
        
        for i in range(len(effect_list1)):
            effect1 = effect_list1[i]
            effect2 = effect_list2[i]
            if effect1[0] != effect2[0]:
                return answer
            
            param_tuple1 = effect1[1]
            param_tuple2 = effect2[1]
            for j in range(len(param_tuple1)):
                param1 = param_tuple1[j]
                if param1 in param_mapping1.keys():
                    param1 = param_mapping1[param1]
                
                param2 = param_tuple2[j]
                if param2 in param_mapping2.keys():
                    param2 = param_mapping2[param2]
                    
                if param1 != param2:
                    return answer
                
        answer = True
        return answer
    
    def choose_probabilistic_action(self, desired_action_signature):
        # retrieve information of desired action
        desired_action_name, desired_param_names = \
            self.services.parser.parse_action(desired_action_signature)
        desired_action = self.deterministic_actions[desired_action_name]
        desired_params = map(self.services.parser.get_object, desired_param_names)
        desired_param_mapping = desired_action.get_param_mapping(desired_params)
        new_desired_param_mapping = {}
        for key in desired_param_mapping.keys():
            new_desired_param_mapping[key] = desired_param_mapping[key][0]
        
        sorted_addlist1 = sorted(desired_action.addlist)
        sorted_dellist1 = sorted(desired_action.dellist)
        # retrieve information of valid actions and compare to desired action
        options = self.services.valid_actions.get()
        relevant_action_tuples = []
        action_score_map = {}
        for option in options:
            action_name, param_names = self.services.parser.parse_action(option)
            action = self.services.parser.actions[action_name]
            params = map(self.services.parser.get_object, param_names)
            param_mapping = action.get_param_mapping(params)
            new_param_mapping = {}
            for key in param_mapping.keys():
                new_param_mapping[key] = param_mapping[key][0]
                
            if isinstance(action, Action):
                sorted_addlist2 = sorted(action.addlist)
                if not self.is_same_effect_list(
                        sorted_addlist1, sorted_addlist2, 
                        new_desired_param_mapping, new_param_mapping):
                    continue
                
                sorted_dellist2 = sorted(action.dellist)
                if not self.is_same_effect_list(
                        sorted_dellist1, sorted_dellist2, 
                        new_desired_param_mapping, new_param_mapping):
                    continue
                
                # found deterministic identical action
                return option
            
            else: # isinstance(action, ProbabilisticAction) == True
                found = False
                index = None
                p1 = 0 # accumulated probability of success
                for i in range(len(action.prob_list)):
                    sorted_addlist2 = sorted(action.addlists[i])
                    if not self.is_same_effect_list(
                            sorted_addlist1, sorted_addlist2, 
                            new_desired_param_mapping, new_param_mapping):
                        continue
                  
                    sorted_dellist2 = sorted(action.dellists[i])
                    if not self.is_same_effect_list(
                            sorted_dellist1, sorted_dellist2, 
                            new_desired_param_mapping, new_param_mapping):
                        continue
                    
                    # found identical action 
                    if found:
                        relevant_action_tuples.remove((option, index, p1))
                        
                    found = True
                    index = i
                    p1 += action.prob_list[i]
                    action_tuple = (option, index, p1)
                    relevant_action_tuples.append(action_tuple)
                
                if found:
                    for i in range(len(action.prob_list)):
                        if action.addlists[i] == [] and action.dellists[i] == []:
                            p2 = action.prob_list[i] # probability of failure
                        
                        else:
                            p2 = 0
                        
                    p3 = 1 - p2 - p1 # probability of undesired effect
                    # calculate score, which is an approximation of the 
                    # expected number of steps to complete the desired action
                    # using the current probabilistic action
                    if p2 != 0 and p3 == 0:
                        score = 1/p1
  
                    elif p2 == 0 and p3 != 0:
                        score = (3 - 2*p1)/p1
                        
                    elif p2 != 0 and p3 != 0:
                        score = (p2/(p2 + p3))/p1 + (p3/(p2 + p3))*((3 - 2*p1)/p1)
                        
                    else: # p1 == 1
                        return option 
                    
                    action_score_map[option] = score
                
        best_score = 1000000 # arbitrary high value, lower is better
        best_action = None
        for (action, score) in action_score_map.items():
            if score < best_score:
                best_score = score
                best_action = action
            
        return best_action
    
    def count_predicates(self, state):
        num_predicates = 0
        for predicate_name in state.keys():
            num_predicates += len(state[predicate_name])
            
        return num_predicates
    
    def update_documentation(self, action_to_apply, deterministic_action = None):
        """ Before applying the action chosen, update relevant data fields for 
        future use (e.g., previous state).
        """
        self.prev_action = action_to_apply
        self.prev_num_predicates = self.curr_num_predicates
        self.prev_state = self.curr_state
        if self.probabilistic_plan_dispatch:
            new_state = self.services.parser.copy_state(self.curr_state)
            self.customized_apply_action_to_state(deterministic_action, new_state)
            self.expected_state = new_state
    
    def customized_apply_action_to_state(self, action_sig, state, check_preconditions=True):
        """ This is a modified version of the standard apply_action_to_state
        method, which uses the derived dictionary self.deterministic_actions
        """
        action_name, param_names = self.services.parser.parse_action(action_sig)
        if action_name.lower() == 'reach-goal':
            return state
        action = self.deterministic_actions[action_name]
        params = map(self.services.parser.get_object, param_names)

        param_mapping = action.get_param_mapping(params)
        if "food" in action_name:
            print "hello"
        if check_preconditions:
            for precondition in action.precondition:
                if not precondition.test(param_mapping, state):
                    raise self.services.parser.PreconditionFalseError()

        if isinstance(action, Action):
            for (predicate_name, entry) in action.to_delete(param_mapping):
                predicate_set = state[predicate_name]
                if entry in predicate_set:
                    predicate_set.remove(entry)

            for (predicate_name, entry) in action.to_add(param_mapping):
                state[predicate_name].add(entry)
    
    def initialize_revealed_predicates(self):
        """ If the revealed predicates file exists then load data from it
        and update the state accordingly, otherwise create an empty template.
        """
        file_path = self.domain + "-" + self.env + "-revealed_predicates"
        if not os.path.isfile(file_path): 
            for predicate_name in self.curr_state.keys():
                self.revealed_predicates[predicate_name] = set([])    
        else:
            with open(file_path) as f:
                saved_dict = json.load(f)
            self.revealed_predicates = self.decode_from_jason(saved_dict)
            self.add_knowledge_revealed()
    
    def get_revealed_predicates(self):
        # find newly added predicates compared to last state
        diff_predicates = {}
        for predicate_name in self.curr_state.keys():
            if len(self.curr_state[predicate_name]) > len(self.prev_state[predicate_name]):
                diff_predicates[predicate_name] = \
                    self.curr_state[predicate_name] - self.prev_state[predicate_name]
        
        # filter out the predicates that could have been added by an action
        action_name, param_names = self.services.parser.parse_action(self.prev_action)
        action = self.services.parser.actions[action_name]
        params = map(self.services.parser.get_object, param_names)
        param_mapping = action.get_param_mapping(params)
        if isinstance(action, Action):
            for (predicate_name, entry) in action.to_add(param_mapping):
                revealed_predicates = \
                    self.remove_possible_added_effects(predicate_name, entry, diff_predicates)

        else: # isinstance(action, ProbabilisticAction) == True
            for i in range(len(action.addlists)):
                if len(action.addlists[i]) > 0:
                    for (predicate_name, entry) in action.to_add(param_mapping, i):
                        revealed_predicates = \
                            self.remove_possible_added_effects(predicate_name, entry, diff_predicates)
           
        return revealed_predicates
    
    def remove_possible_added_effects(self, predicate_name, entry, diff_predicates):
        """ This is an auxiliary function supporting get_revealed_predicates()
        """
        if predicate_name in diff_predicates.keys():
            if entry in diff_predicates[predicate_name]:
                diff_predicates[predicate_name].remove(entry)
        
        return diff_predicates
    
    def update_revealed_predicates(self, revealed_predicates):
        for predicate_name in revealed_predicates.keys():
            for entry in revealed_predicates[predicate_name]:
                self.revealed_predicates[predicate_name].add(entry)
                
    def encode_for_jason(self, predicate_dict):
        new_dict = {}
        for (key, value) in predicate_dict.items():
            new_dict[key] = list(value)
        
        return new_dict
    
    def decode_from_jason(self, predicate_dict):
        new_dict = {}
        for (key, value_lists) in predicate_dict.items():
            new_dict[key] = set([])
            for value_list in value_lists:
                new_tuple = tuple(value_list)
                new_dict[key].add(new_tuple)
        
        return new_dict
    
    def add_knowledge_revealed(self):
        for (predicate_name, set_of_tuples) in self.revealed_predicates.items():
            if len(set_of_tuples) > 0:    
                for entry_tuple in set_of_tuples:
                    self.curr_state[predicate_name].add(entry_tuple)
                    
    def generate_domain(self, path, actions):
        """ This is an auxiliary function which generates deterministic domain 
        files according to the provided predicates and actions.
        """
        domain_str = "(define (domain " + self.domain + ")\n"
        domain_str += "(:predicates\n\t"
        for obj in self.services.parser.task.predicates:
            if not obj.name =="=":
                predicate = "(" + obj.name
                for i in range(len(obj.arguments)):
                    predicate += " ?p" + str(i)
                predicate += ")"
                domain_str += predicate + " "

        domain_str += "\n)\n"
        for (name, action) in actions.items(): 
            action_str = "(:action " + name + "\n"
            action_str += " :parameters ("
            for parameter_tuple in action.signature:
                action_str += " " + parameter_tuple[0]
            
            action_str += ")\n :precondition\n\t(and "
            for obj in action.precondition:
                predicate = "(" + obj.name
                for param in obj.signature:
                    predicate += " " + param

                predicate += ")"
                if obj.negated:
                    action_str += "(not " + predicate + ") "
                else:
                    action_str += predicate + " "
            
            action_str += ")\n :effect\n\t(and "
            
            for predicate_tuple in action.addlist:
                predicate = "(" + predicate_tuple[0]
                for param in predicate_tuple[1]:
                    predicate += " " + param

                predicate += ")"
                action_str += predicate + " "
                
            for predicate_tuple in action.dellist:
                predicate = "(" + predicate_tuple[0]
                for param in predicate_tuple[1]:
                    predicate += " " + param

                predicate += ")"
                action_str += "(not " + predicate + ") "
            
            action_str += "))\n"
            domain_str += action_str  
            
        domain_str += ")"
        with open(path, 'w') as f:
            f.write(domain_str)


# run the executor
print LocalSimulator().run(domain_path, problem_path, PRE_Executor())










