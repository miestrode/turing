import random, sys
from pddlsim.executors.executor import Executor
import json
import os.path
import math
from utils import parser, valid_actions_custom
from utils.knowledge_graph import KnowldegeGraph
from utils.goal_tracking_custom import GoalTrackingCustom
import atexit
import numpy as np
from collections import Counter
import utils.file_manager as fm

class GraphLearner(Executor):
    """ GraphLearner - find the best policy for solving problems """
    def __init__(self, is_ojt = False):
        self.successor = None
        self.is_ojt = is_ojt

        if not self.is_ojt:
            atexit.register(self.__save_information)
    
    def initialize(self, services):
        self.services = services
        self.goal_tracking_custom = GoalTrackingCustom(self.services)

        self.states_history_capacity = 15
        self.states_repetition_threshold = 5

        self.__init_learning_params()
        self.__init_knowledge_graph()
        self.__init_goals()
        self.__learn()

    def __init_learning_params(self):
        self.num_of_episodes = 10
        self.max_steps_per_episode = 1000

        self.min_exploration_rate = 0.01
        self.exploration_rate = 1
        self.max_exploration_rate = self.exploration_rate
        self.exploration_decay_rate = 0.008
        self.min_learning_rate = 0.1
        self.learning_rate = 0.5
        self.max_learning_rate = self.learning_rate
        self.learning_decay_rate = 0.008
        self.discount_factor = 0.9

        self.q_table = {}
        self.starting_step = 0
        self.__load_learning_params()
            
    def __load_learning_params(self):
        try:
            self.q_table, self.starting_step, self.exploration_rate, self.learning_rate \
                = fm.load_learning_params_file(self.services)
        except IOError:
            return

    def __init_knowledge_graph(self):
        try:
            self.graph = fm.load_knowledge_graph(self.services)
        except IOError:
            self.graph = KnowldegeGraph(self.services)
    
    def __init_goals(self):
        self.goals = {}

        try:
            goal_hash = fm.load_policy_file(self.services)[1]
            if goal_hash != None:
                self.goals[goal_hash] = False
        except IOError:
            return

    def __learn(self):
        for episode in range(self.num_of_episodes):
            self.current_episode = episode
            current_state = self.__rest_env()

            for step in range(self.max_steps_per_episode):
                self.current_step = step
                
                # Print progress
                solution_found_indicator = '(*)' if len(self.goals) else ''
                print "LEARNING: ", (step + episode*self.max_steps_per_episode)\
                     * 100 / (self.num_of_episodes * self.max_steps_per_episode), '%', solution_found_indicator,'\r',
                sys.stdout.flush()

                # get actions for current state
                current_state_hash = parser.state_to_hash(current_state)
                self.__add_state_if_new(current_state_hash)
                action = self.__get_next_action(current_state, current_state_hash)
                self.__add_action_if_new(current_state_hash, action)
                
                # apply action
                old_state_hash = current_state_hash
                reward, done = self.__apply_action(action, current_state)
                new_state_hash = parser.state_to_hash(current_state)
                self.__add_state_if_new(new_state_hash)
                
                if action != None:
                    # Update q table with old and new state and action performed
                    self.__update_q_table(old_state_hash, action, new_state_hash, reward)
                
                if done:
                    # Reset completed goals and continue learning
                    self.goal_tracking_custom.reset()
                    # Used for learning on the run
                    if self.is_ojt:
                        self.__save_information()
                        return
                elif action == None:
                    # We have nothing to do in this state -> abort
                    break

                if action != None:
                     # Save actions and states history
                    self.__add_to_history(old_state_hash, action)

            # Decay exploration and learning rates
            self.exploration_rate = self.__get_updated_rate(self.exploration_rate, self.min_exploration_rate, self.max_exploration_rate, self.exploration_decay_rate)
            self.learning_rate = self.__get_updated_rate(self.learning_rate, self.min_learning_rate, self.max_learning_rate, self.learning_decay_rate)

    def __update_q_table(self, state_hash, action, new_state_hash, reward):
        best_action =  self.__get_best_action(new_state_hash) if new_state_hash != None else None
        best_action_q = self.q_table[new_state_hash][best_action] if new_state_hash != None and best_action != None else 0

        self.q_table[state_hash][action] = self.q_table[state_hash][action] * (1 - self.learning_rate) \
            + self.learning_rate * (reward + self.discount_factor * best_action_q)

    def __add_to_history(self, state_hash, action):
        # Save actions and states history for avoiding the past

        # If the queue is full -> pop the first item out
        if self.states_history_capacity != None \
            and len(self.states_hashes_history) + 1 > self.states_history_capacity:
            self.states_hashes_history.pop(0)
            self.actions_history.pop(0)

        self.states_hashes_history.append(state_hash)
        self.actions_history.append(action)

        # Update the states repetition counter
        self.states_history_counter = Counter(self.states_hashes_history)

    def __rest_env(self):
        # Reset goal properties
        self.goal_tracking_custom.reset()
        for goal in self.goals:
            self.goals[goal] = False
        self.__refresh_current_goal()

        # Reset history
        state = self.services.perception.get_state()
        self.states_hashes_history = []
        self.actions_history = []
        self.states_history_counter = Counter(self.states_hashes_history)

        return state

    def __get_next_action(self, state, state_hash = None):
        if state_hash == None:
            state_hash = parser.state_to_hash(state)

        # Explore vs Exploit
        if len(self.q_table[state_hash].keys()):
            exploit_prob = random.uniform(0, 1)
            if exploit_prob > self.exploration_rate:
                # exploit
                action = self.__get_best_action(state_hash)
                return action

        # explore
        valid_actions = valid_actions_custom.get_valid_actions(self.services, state)
        if(len(valid_actions) == 0):
            return None
        
        # Get the action that will take us to a new state
        action = self.__get_lru_state_action(valid_actions, state)
        return action

    def __get_lru_state_action(self, actions, state):
        # Run all the action available and store the new states as hash after each action
        states_hashes = []
        for action in actions:
            state_copy = self.services.parser.copy_state(state)
            state_copy_hash = self.__get_next_state_hash(state_copy, action)
            states_hashes.append(state_copy_hash)

        # Calculate states_hashes counters
        probs = []
        for s in states_hashes:
            if s in self.states_history_counter:
                probs.append(-self.states_history_counter[s])
            else:
                probs.append(0)

        # More frequent state gets lower probs. New and least frequent states gets higher probs
        probs_exp = np.exp(probs)
        probs = probs_exp/sum(probs_exp)
        
        # Choose action by probabilities (probs)
        action = np.random.choice(actions, size=1, replace=False, p=probs)[0]
        return action

    def __get_best_action(self, state):
        if not len(self.q_table[state].keys()):
            return None
        return max(self.q_table[state], key=self.q_table[state].get)

    def __get_best_policy(self):
        policy = {}
        shortest_path_len = sys.maxint
        min_prob_ratio = sys.maxint
        shortest_goal_hash = None

        current_state = self.services.perception.get_state()
        state_hash = parser.state_to_hash(current_state)

        if not self.graph.is_contains(state_hash):
            return None, None, None

        # All the goals are the same one but with different artifacts, find the shortest path among them
        for goal_hash in self.goals:
            if not self.graph.is_contains(goal_hash):
                continue 

            policy[goal_hash] = self.graph.find_shortest_path(state_hash, goal_hash)
            if policy[goal_hash] == None:
                continue

            # If the domain isn't deterministic, find the path with the best probs (smallest probs ratio)
            prob_ratio = 0
            for index in policy[goal_hash]:
                action = policy[goal_hash][index]
                prob_ratio += parser.get_action_prob_ratio(self.services, action)

            # All ways lead to Rome, find the shortest one
            path_len = len(policy[goal_hash])
            if path_len < shortest_path_len and path_len > 1:
                if prob_ratio < min_prob_ratio:
                    shortest_path_len = path_len
                    shortest_goal_hash = goal_hash
                    min_prob_ratio = prob_ratio
        
        if shortest_goal_hash == None:
            return None, None, None

        return policy[shortest_goal_hash], shortest_goal_hash, min_prob_ratio

    def __add_state_if_new(self, state_hash):
        if state_hash not in self.q_table:
            self.q_table[state_hash] = {}

    def __add_action_if_new(self, state_hash, action):
        if action != None and action not in self.q_table[state_hash]:
            self.q_table[state_hash][action] = 0

    def __apply_action(self, action, state, state_hash = None):
        old_state_hash = parser.state_to_hash(state) if state_hash == None else state_hash
        new_state_hash = None

        if action != None:
            new_state_hash = self.__get_next_state_hash(state, action)
            # Store this new knowledge: old_state_hash -> (action) -> new_state_hash
            self.graph.link(old_state_hash, new_state_hash, action)

        reward = self.__get_reward(old_state_hash, state, action, state_hash = new_state_hash)
        # Back propogate the reward (with respect to the distance from current state to each state)
        self.__backpropogate(reward)

        done = self.goal_tracking_custom.reached_all_goals(state)
            
        return reward, done

    def __get_next_state_hash(self, state, action):
        # Apply action on state and return hashed new state

        self.services.parser.apply_action_to_state(action, state, False)
        self.services.parser.apply_revealable_predicates(state)
        self.goal_tracking_custom.on_action()

        return parser.state_to_hash(state)

    def __backpropogate(self, base_reward):
        # Back propogate the base_reward (with respect to the distance from current state to each state back)
        for i in range(0, len(self.states_hashes_history) - 1):
            action = self.actions_history[i]
            old_state = self.states_hashes_history[i]
            new_state = self.states_hashes_history[i + 1]
            reward = base_reward * math.exp(-((self.states_history_capacity * 1.0) / 2) / (i+1))
            self.__update_q_table(old_state, action, new_state, reward)

    def __refresh_current_goal(self):
        # Set the current goal to be the next uncompleted goal (we know about)
        try:
            self.current_goal = self.goals.keys()[self.goals.values().index(False)]
        except ValueError:
            self.current_goal = None

    def __get_reward(self, old_state_hash, state, action, state_hash = None):
        if action == None:
            self.__refresh_current_goal()
            return -10

        if state_hash == None:
            state_hash = parser.state_to_hash(state)
        
        done = self.goal_tracking_custom.reached_all_goals(state)

        if done:
            # Save this goal (as knowledge)
            self.goals[state_hash] = True
            # Find next goal
            self.__refresh_current_goal()

        # R Max
        if self.states_history_counter[old_state_hash] >= self.states_repetition_threshold:
            q_value = self.q_table[old_state_hash][action]
            reward = float(q_value) / self.states_history_counter[old_state_hash]
            return reward * 10

        # Punish for repeating on states
        repeat_punishment = 0.05 if not self.__is_new_state(state_hash) else 0
        return -0.04 - repeat_punishment

    def __is_new_state(self, state_hash):
        return state_hash not in self.states_hashes_history
            
    def __get_updated_rate(self, rate, min, max, decay):
        # Update 'rate' by 'decay'

        if abs(rate - min) <= decay:
            self.current_episode = 0
            self.starting_step = 0

        steps_count = self.current_episode + self.starting_step
        
        updated_rate = min + (max - min) * math.exp(-decay * steps_count)
        return updated_rate

    def __save_information(self):
        self.__save_policy()
        self.__save_knowledge()
        self.__save_learning_params()

    def __save_policy(self):
        # Save policy to file

        policy, goal, prob_ratio = self.__get_best_policy()
        fm.save_policy(self.services, policy, goal, prob_ratio)
        
    def __save_knowledge(self):
        # Save knowledge graph to file

        fm.save_knowledge(self.services, self.graph.to_json())

    def __save_learning_params(self):
        # Save learning params to file
        
        fm.save_learning_params(self.services, self.q_table,\
                                 self.current_episode, self.exploration_rate, self.learning_rate)

    def next_action(self):
        return None
