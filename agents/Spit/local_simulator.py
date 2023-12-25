from simulator import Simulator
from pddlsim.fd_parser import FDParser
from pddlsim.services.simulator_services import SimulatorServices


class LocalSimulator:
    def __init__(self, print_actions=True, planner=None, hide_fails=False, hide_probabilstics=False):
        self.print_actions = print_actions
        self.planner = planner
        self.hide_fails = hide_fails
        self.hide_probabilistics = hide_probabilstics

    def run(self, domain_path, problem_path, executive):
        parser = FDParser(domain_path, problem_path)
        sim = Simulator(parser)
        service_parser = parser
        if self.hide_fails or self.hide_probabilistics:
            service_parser = parser.get_obscure_copy(hide_fails=self.hide_fails,
                                                     hide_probabilistics=self.hide_probabilistics)
        mediator = SimulatorServices(
            service_parser, sim.perceive_state, self.planner)
        executive.initialize(mediator, sim)
        self.previous_action = None

        def next_action():
            if self.print_actions and sim.action_failed:
                print " -failed- "
            if self.previous_action and not sim.action_failed:
                mediator.on_action(self.previous_action)
            self.previous_action = executive.next_action()
            if self.print_actions and self.previous_action:
                print self.previous_action

            return self.previous_action

        return sim.simulate(next_action)
