class StateList:
    def __init__(self):
        self.stateMap = dict()
        self.topologic = dict()
        self.visited = dict()
        self.treshhold = 10

    def get_state_key(self, state):
        if state not in self.stateMap.values():
            self.stateMap[len(self.stateMap)] = state
        key = self.stateMap.values().index(state)
        return key

    def add_to_map(self, state, action, next_state):
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        if state_key not in self.topologic:
            self.topologic[state_key] = {}
        if action not in self.topologic[state_key]:
            self.topologic[state_key][action] = {}
        if next_state_key not in self.topologic[state_key][action]:
            self.topologic[state_key][action][next_state_key] = {"count": 0}
        self.topologic[state_key][action][next_state_key]["count"] += 1

    def get_next_state_by_action(self, state, action):
        state_key = self.get_state_key(state)
        next_states = self.topologic[state_key][action]
        max_count = 0
        next_state = None
        for ns in next_states:
            if ns["count"] > max_count:
                max_count = ns["count"]
                next_state = ns.key()
        if next_state is None:
            return None
        return self.stateMap[next_state]

    def get_next_action(self, state):
        state_key = self.get_state_key(state)
        if state_key not in self.topologic:
            return None
        next_action = None
        for action in self.topologic[state_key]:
            if self.get_next_state_by_action(state, action.key()) not in self.visited:
                return action.key()
        return None

    def get_next_states(self, state, action):
        state_key = self.get_state_key(state)
        if state_key not in self.topologic.keys():
            self.topologic[state_key] = {}
        if action not in self.topologic[state_key].keys():
            self.topologic[state_key][action] = {}
        return self.topologic[state_key][action]

    def get_state_visited_by_action(self, state, action):
        next_states = self.get_next_states(state, action)
        visit = []
        view = []
        sum_view = 0
        for ns in next_states:
            if ns in self.visited.keys():
                visit += [self.visited[ns]]
            else:
                visit += [0]
            view += [next_states[ns]["count"]]
            sum_view += next_states[ns]["count"]
        value = 0
        for vi, vw in zip(visit, view):
            value += float(vi) * float(float(vw) / float(sum_view))
        return value

    def add_to_visited(self, state):
        state_key = self.get_state_key(state)
        if state_key not in self.visited.keys():
            self.visited[state_key] = 0
        self.visited[state_key] += 1
