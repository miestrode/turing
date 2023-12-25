import os
import sys

from pddlsim.fd_parser import FDParser
from pddlsim.local_simulator import LocalSimulator

from src.agents.plbp_agent import PLBPAgnet
from src.editors.domain_editor import DomainEditor
from src.handlers.probabilities_learning_handler import ProbabilitiesLearningHandler
from src.handlers.reveal_learning_handler import RevealLearningHandler


def is_running_from_cli(argv):
    return len(argv) > 1


def create_folders(folders):
    for folder in folders:
        if not os.path.exists(folder):
            os.mkdir(folder)


def main():
    if is_running_from_cli(sys.argv):
        mode = sys.argv[1]
        domain_path = sys.argv[2]
        problem_path = sys.argv[3]
    else:
        mode = '-E'
        domain_path = 'pddl_files/satellite_domain_multi.pddl'
        problem_path = 'pddl_files/satellite_problem_multi.pddl'

    create_folders([DomainEditor.DETERMINISTIC_DOMAIN_DIRECTORY, 'probabilities', 'reveals'])

    parser = FDParser(domain_path, problem_path)
    probabilities_learning_handler = ProbabilitiesLearningHandler('probabilities/' + parser.domain_name, parser.actions)
    reveal_learning_handler = RevealLearningHandler('reveals/' + parser.domain_name)

    if not os.path.isfile(DomainEditor.get_deterministic_domain_path(domain_path)):
        DomainEditor.write_deterministic_domain_from_stochastic_domain(parser)

    agent = PLBPAgnet(probabilities_learning_handler, reveal_learning_handler, mode)

    print LocalSimulator().run(domain_path, problem_path, agent)


if __name__ == '__main__':
    main()
