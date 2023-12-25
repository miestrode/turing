from pddlsim.executors.executor import Executor
from utils import parser
from graph_executer import GraphExecuter
from pddlsim.executors.plan_dispatch import PlanDispatcher

class ExecuterManager(Executor):
    """ExecuterManager manage which executer should we run according to the given domain"""
    def __init__(self):
        self.successor = None

    def initialize(self, services):
        self.services = services
        
        is_determinisitc = parser.is_deterministic_domain(self.services)
        # If the domain is deterministic run the planner, otherwise run the graph executer (that use learning knowledge)
        self.executer = PlanDispatcher() if is_determinisitc else GraphExecuter()
        if is_determinisitc:
            print "Planning..."
        self.executer.initialize(self.services)

    def next_action(self):
        return self.executer.next_action()
