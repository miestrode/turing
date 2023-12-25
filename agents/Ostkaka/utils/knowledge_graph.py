from utils.graph import Graph
from pddlsim.parser_independent import PDDL


class KnowldegeGraph:
    def __init__(self, services, json=None):
        self.services = services

        self.graph = Graph(json=json, weighted=False)

    def link(self, frm, to, action):
        # Add link between 'frm' and 'to' through 'action'
        self.graph.add_edge(frm, to, e_data={"action": action}, is_unique=True)

    def is_contains(self, v):
        return self.graph.get_vertex(v) != None

    def find_shortest_path(self, source, target):
        actions = {}
        path = self.graph.find_shortest_path(source, target)

        # If we can't find a path from sourec to target -> return None
        if len(path) <= 1:
            return None

        # Arrange dictionary of actions to perform per state
        for v in path:
            edge_info = v["e"]
            if edge_info is None:
                break
            action = edge_info["action"]
            v_id = v["v"].id
            actions[v_id] = action

        return actions

    """ option: 
                0 - display all
                1 - display only vertiex
                2 - display only connections (edges)"""

    def display(self, option=0):
        self.graph.display(option)

    def to_json(self):
        return self.graph.to_json()
