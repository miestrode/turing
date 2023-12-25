import random
import sys
import os
import datetime
import time

class MyExecutive(object):

	def __init__(self, mode, environment, problem):
		self.succcessor = None
		self.environment = environment
		self.problem = problem
		self.mode = mode
		self.last_mapped_state_index = -1
		self.time = datetime.datetime.now()

	def initialize(self,services):
		self.services = services
		self.visited_states = []
		self.visited_actions = []
		self.policy_file_path = self.services.parser.domain_name + "_" + self.environment + ".policy"
		self.policy = self.load_policy_file()

	def next_action(self):
		self.learn_mapping_by_timer()

		chosen_action = self.choose_action()

		return chosen_action

	def learn_mapping_by_timer(self):
		state = self.services.perception.get_state()
		self.visited_states.append(state)

		time_diff = datetime.datetime.now() - self.time
		if time_diff.seconds > 10:
			self.learnMapping()

	def state_as_string(self, state):
		result = "{"
		for key in sorted(state.keys()):
			if result != "{":
				result += ", "
			result += "'" + key + "': "
			result += str(sorted(state[key]))
		result += "}"
		return result

	def choose_action(self):
		# finished all goals
		if self.services.goal_tracking.reached_all_goals():
			self.learnMapping()
			self.learnRewards()
			return None

		# no valid actions
		valid_actions = self.services.valid_actions.get()
		if len(valid_actions) == 0: return None

		# choose action
		chosen_action = None

		problem_policy = self.policy.get(self.problem, {})
		policy_number_of_runs = problem_policy.get("number_of_learn_runs", 0)

		if self.mode == "-L" or len(self.visited_actions) > 4000 or policy_number_of_runs == 0:
			chosen_action = self.explore(valid_actions)
		else:
			chosen_action = self.exploit(valid_actions)

		if chosen_action != None:
			self.visited_actions.append(chosen_action)

		return chosen_action

	def explore(self, valid_actions):
		return self.choose_random_action_prefer_unvisited(valid_actions)

	def get_state_policy_mapping(self):
		state = self.services.perception.get_state()
		policy_mapping = self.policy.get("mapping", {})
		return policy_mapping.get(self.state_as_string(state))

	def exploit(self, valid_actions):
		state_policy_mapping = self.get_state_policy_mapping()
		problem_policy = self.policy.get(self.problem, {})

		# if state is not mapped, explore it
		if state_policy_mapping == None:
			return self.explore(valid_actions)

		best_actions = []
		best_policy_value = sys.maxint

		for action in valid_actions:
			state_action_policy_values = state_policy_mapping.get(action, {})
			action_accumulated_reward = 0
			action_occurences = 0
			action_reward = 0
			for next_state, next_state_occurence in state_action_policy_values.iteritems():
				next_state_policy_distance = problem_policy.get(next_state, 0)
				action_accumulated_reward += next_state_policy_distance * next_state_occurence
				action_occurences += next_state_occurence
			if action_occurences > 0:
				action_reward = action_accumulated_reward / action_occurences

			if action_reward == best_policy_value:
				best_actions.append(action)
			elif action_reward < best_policy_value:
				best_policy_value = action_reward
				best_actions = [action]

		return self.choose_random_action_prefer_unvisited(best_actions)

	def choose_random_action_prefer_unvisited(self, actions):
		chosen = random.choice(actions)

		actions_sum_of_occurences = 0
		for action in actions:
			action_visit_count = self.visited_actions.count(action)
			actions_sum_of_occurences += action_visit_count

		actions_to_choose_from = []
		for action in actions:
			action_visit_count = self.visited_actions.count(action)
			number_of_times = actions_sum_of_occurences - action_visit_count
			for i in range(number_of_times):
				actions_to_choose_from.append(action)

		if len(actions_to_choose_from) > 0:
			chosen = random.choice(actions_to_choose_from)

		return chosen

	def learnMapping(self):
		if self.mode == "-E": return

		# learn environment mapping
		mapping = self.policy.get("mapping", {})
		for index, state in enumerate(self.visited_states):
			if index > self.last_mapped_state_index and index < len(self.visited_actions):
				next_state = self.visited_states[index+1]
				action = self.visited_actions[index]
				state_mapping = mapping.get(self.state_as_string(state), {})
				action_mapping = state_mapping.get(action, {})
				next_state_value = action_mapping.get(self.state_as_string(next_state), 0)
				next_state_value += 1
				action_mapping[self.state_as_string(next_state)] = next_state_value
				state_mapping[action] = action_mapping
				mapping[self.state_as_string(state)] = state_mapping
				self.last_mapped_state_index = index
		self.policy["mapping"] = mapping

		self.save_policy_file()
		self.time = datetime.datetime.now()

	def learnRewards(self):
		if self.mode == "-E": return

		# learn distance to goal [state]
		number_of_steps = len(self.visited_actions)
		distances_to_goal = {}
		for index, state in enumerate(self.visited_states):
			if index < len(self.visited_actions):
				goal_distance_for_state = number_of_steps - index
				distances_to_goal[self.state_as_string(state)] = goal_distance_for_state

		problem_policy = self.policy.get(self.problem, {})

		for state_string, distance in distances_to_goal.iteritems():
			policy_value_for_state = problem_policy.get(state_string, 0)
			policy_value_for_state += distance
			problem_policy[state_string] = policy_value_for_state

		# learn number of runs
		policy_number_of_runs = problem_policy.get("number_of_learn_runs", 0)
		policy_number_of_runs += 1
		problem_policy["number_of_learn_runs"] = policy_number_of_runs

		self.policy[self.problem] = problem_policy
		self.save_policy_file()

	def save_policy_file(self):
		f = open(self.policy_file_path, 'w')
		f.write(str(self.policy))
		f.close()

	def load_policy_file(self):
		policy = {}
		if os.path.isfile(self.policy_file_path):
			s = open(self.policy_file_path, 'r').read()
			policy = eval(s)
		return policy

from pddlsim.local_simulator import LocalSimulator
mode = sys.argv[1]
domain_path = sys.argv[2]
problem_path = sys.argv[3]
if "-" in problem_path:
	environment, problem = problem_path.replace(".pddl", "").split("-")
else:
	environment, problem = domain_path.replace(".pddl", ""), problem_path.replace(".pddl", "")
if mode == "-L":
	exploreProbability = 0.75
	r = random.uniform(0, 1)
	if r > exploreProbability:
		mode = "-R"
my_executive = MyExecutive(mode, environment, problem)
print LocalSimulator().run(domain_path, problem_path, my_executive)
