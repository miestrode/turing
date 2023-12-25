# Name: Yehonatan Sofri
# ID:   205433329


class QTable:
    def __init__(self):
        self.table = {}

    def set_table(self, table=None):
        if table is not None:
            self.table = table
        else:
            self.table = {}

    def get_table(self):
        return self.table

    def get_value(self, state, action):
        value = 0

        if not isinstance(state, str):
            state = str(state)
        if state in self.table and action in self.table[state]:
            value = self.table[state][action]
        return value

    def _set_max_in_entry(self, state, action_name, value):
        if not isinstance(state, str):
            state = str(state)
        self.table[state]["max_value"] = value
        self.table[state]["max_action"] = action_name

    def _create_entry(self, state, action_name, value):
        if not isinstance(state, str):
            state = str(state)
        self.table[state] = {}
        self._set_max_in_entry(state, action_name, value)

    def set_entry(self, state, action_name, value):
        if not isinstance(state, str):
            state = str(state)

        if state not in self.table:
            self._create_entry(state, action_name, value)
        elif value > self.table[state]["max_value"]:
            self._set_max_in_entry(state, action_name, value)
        self.table[state][action_name] = value

    def get_max_value_from_state(self, state):
        value = 0

        if not isinstance(state, str):
            state = str(state)

        if state in self.table and "max_value" in self.table[state]:
            value = self.table[state]["max_value"]
        return value

    def get_max_action_from_state(self, state):
        action = None

        if not isinstance(state, str):
            state = str(state)

        if state in self.table.keys() and "max_action" in self.table[state]:
            action = self.table[state]["max_action"]
        return action

    def action_list_to_string(self, action_list):
        action_list.sort()
        return "".join(action_list)

    @staticmethod
    def make_new_table():
        table = {}
