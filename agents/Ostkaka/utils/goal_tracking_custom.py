import copy
from utils import parser
from pddlsim.parser_independent import Conjunction

"""
    A copy of GoalTracking class but with a custom 'reached_all_goals' function that
    checks for goals at given state and for sub-goals aswell.
"""


class GoalTrackingCustom:
    def __init__(self, services):
        self.services = services
        self.__initialize()

    def reached_all_goals(self, state=None, with_subgoals=False):
        if self.dirty:
            if state == None:
                state = self.services.perception.get_state()
            self._check_goal(state)
            current_completed_subgoals = self.__count_completed_subgoals(state)
            is_subgoal_completed = (
                current_completed_subgoals > self.__last_completed_subgoals_count
            )
            self.__last_completed_subgoals_count = current_completed_subgoals
            self.dirty = False
            if with_subgoals:
                return not self.uncompleted_goals, is_subgoal_completed
            return not self.uncompleted_goals
        if with_subgoals:
            return not self.uncompleted_goals, False
        return not self.uncompleted_goals

    def on_action(self):
        self.dirty = True

    def reset(self):
        self.__initialize()

    def __initialize(self):
        self.dirty = self.services.goal_tracking.dirty
        self.completed_goals = copy.deepcopy(
            self.services.goal_tracking.completed_goals
        )
        self.uncompleted_goals = copy.deepcopy(
            self.services.goal_tracking.uncompleted_goals
        )

        self.__uncompleted_subgoals = parser.flat_goals(self.uncompleted_goals)
        self.__last_completed_subgoals_count = 0

    def __count_completed_subgoals(self, state):
        done_subgoals = list()
        for subgoal in self.__uncompleted_subgoals:
            done_subgoal = subgoal.test(state)
            if done_subgoal:
                done_subgoals.append(subgoal)
        return len(done_subgoals)

    def _check_goal(self, state):
        to_remove = list()
        for goal in self.uncompleted_goals:
            done_subgoal = self.services.parser.test_condition(goal, state)
            if done_subgoal:
                to_remove.append(goal)
        for goal in to_remove:
            self.uncompleted_goals.remove(goal)
            self.completed_goals.append(goal)
