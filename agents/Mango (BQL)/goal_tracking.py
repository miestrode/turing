# Name: Yehonatan Sofri
# ID:   205433329


class GoalTracking:

    """
    A service to keep track of completed and uncompleted goals
    This is very useful for situations with multiple goals
    Note that this will use perception for each round in order to check goals were accomplished at the current state
    """

    def __init__(self, parser, perception):
        self.parser = parser
        self.perception = perception
        self.completed_goals = []
        self.uncompleted_goals = self.parser.goals[:]
        self.dirty = True

    def on_action(self, action, state=None):
        self.dirty = True
        self.reached_all_goals(state)

    def has_multiple_goals(self):
        return len(self.uncompleted_goals) > 1

    def reached_all_goals(self, state=None):
        if self.dirty:
            self._check_goal(state)
            self.dirty = False
        return not self.uncompleted_goals

    def _check_goal(self, state=None):
        current_state = state if state is not None else self.perception.get_state()
        to_remove = list()
        for goal in self.uncompleted_goals:
            done_subgoal = self.parser.test_condition(goal, current_state)
            if done_subgoal:
                to_remove.append(goal)
        for goal in to_remove:
            self.uncompleted_goals.remove(goal)
            self.completed_goals.append(goal)
