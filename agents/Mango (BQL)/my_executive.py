# Name: Yehonatan Sofri
# ID:   205433329
import pddlsim.parser_independent as prs
from pddlsim.fd_parser import FDParser
from pddlsim import local_simulator
from pddlsim import planner
import io_handler
import qlearning
import hashlib
import mcts
import sys
import os


success_threshold = 200
metadata_f_name = "my_executive_metadata"
results_file_name = "results.csv"
planner_suffix = " plan"


class ProblemOrganizer:
    """
    a class to get data about a problem without doing akk the procedures of pddlsim.
    also serve as an agent - make sure to inject plan is given
    """

    def __init__(self, my_domain_path, my_problem_path, plan=[]):
        self.parser = FDParser(my_domain_path, my_problem_path)
        self.domain_name = self.parser.domain_name
        self.problem_name = self.parser.problem_name
        self.goals = self.get_goals()
        self.determinism = 0
        self.plan = plan

    def initialize(self, services):
        pass

    def next_action(self):
        action = None
        if self.plan:
            action = self.plan.pop(0)
        return action

    def get_goals(self):
        li = []

        if len(self.parser.goals) is 1:
            if isinstance(self.parser.goals[0], prs.Literal):
                li = sorted([self.literal_to_string(self.parser.goals[0])])
            else:
                for literal in self.parser.goals[0].parts:
                    li.append(self.literal_to_string(literal))
                li = sorted(li)
        else:
            li = sorted([self.literal_to_string(goal)
                         for goal in self.parser.goals])
        return li

    @staticmethod
    def goals_inclusion(set_1, list_2):
        return set_1.issubset(list_2)

    @staticmethod
    def get_exact_same_problem(dom_path, prob_path, data_obj):
        new_problem = ProblemOrganizer(dom_path, prob_path)

        if new_problem.domain_name in data_obj.keys():
            for tup in data_obj[new_problem.domain_name]:
                first_goals = ProblemOrganizer.goals_hash(tup[2])
                new_goals = ProblemOrganizer.goals_hash(new_problem.goals)
                if first_goals == new_goals:
                    return new_problem.domain_name + str(first_goals)
        return None

    @staticmethod
    def get_similar_problem_file_name(new_domain_path, new_problem_path, data_obj):
        """
        check if has knowledge about problem - same one or problem with same goals.
        :param new_domain_path: string
        :param new_problem_path: string
        :param data_obj: metadata object, dictionary where keys are domain names,
        values are lists of information about problem.
        :return: name of problem/ similar problem or None if not exist.
        """
        res = None
        new_problem = ProblemOrganizer(new_domain_path, new_problem_path)

        # if domain is known in metadata, iterate on every information element
        if new_problem.domain_name in data_obj.keys():
            for tup in data_obj[new_problem.domain_name]:
                # if both has exact pproblem name - return it!
                if tup[0] == new_problem.problem_name:
                    return new_problem.domain_name \
                           + str(ProblemOrganizer.goals_hash(tup[2]))
                if ProblemOrganizer.goals_inclusion(set(new_problem.goals), tup[2]):
                    helper = ProblemOrganizer(domain_path, tup[1])
                    res = new_problem.domain_name + str(ProblemOrganizer.goals_hash(helper.goals))
        return res

    @staticmethod
    def literal_to_string(literal):
        """
        :param literal: some kind of goal object.
        :return: string representation
        """
        res = None
        if isinstance(literal, prs.Literal):
            return literal.predicate + str(literal.args)
        elif isinstance(literal, prs.Disjunction):
            res = "OR"
        else:
            res = "AND"

        for part in literal.parts:
            part_str = ProblemOrganizer.literal_to_string(part)
            res += part_str
        return res


    @staticmethod
    def goals_hash(goals_list):
        """
        :return: sorted list of goals
        """
        hash_object = hashlib.sha1(str(goals_list))
        return hash_object.hexdigest()

    @staticmethod
    def get_determinism(dom_path, prob_path):
        """
        check if domain is deterministic
        :param dom_path: path to domain file
        :param prob_path: path to problem file
        :return: boolean, true if domain is deterministic
        """
        dummy_helper = ProblemOrganizer(dom_path, prob_path)
        for action in dummy_helper.parser.actions:
            try:
                var = dummy_helper.parser.actions[action].prob_list
                return False
            except:
                pass

        return True


def try_planner():
    """
    try make a plan using the default planner.
    :return: boolean, True if planner returned a plan
    """
    plan = None
    try:
        plan = planner.make_plan(domain_path, problem_path)
    except:
        plan = None

    return plan


def add_to_metadata(tup, dom_name, metadata_obj):
    """
    add a new information element to metadata
    :param tup: tuple of problem name, file name and goals list.
    :param dom_name: string, name of domain
    :param metadata_obj: a dictionary with all information about problems.
    """
    if dom_name in metadata_obj.keys():
        for tmp_tuple in metadata_obj[dom_name]:
            if tmp_tuple[0] == tup[0]:
                return metadata_obj
        metadata_obj[dom_name].append(tup)
    else:
        metadata_obj[dom_name] = [tup]

    return metadata_obj


def learn(metadata_obj, to_fork=True):
    """
    run a learning iteration.
    check if a problem with same goals exist.
    if so - learn on the already made data with it.
    run qlearning in child process and MCTS on current process.
    save changes in metadata and write it to file.
    :param metadata_obj: object that contain data about all learned problems.
    :param to_fork: boolean to mention if learning should be full or not
    """
    data_helper = ProblemOrganizer(domain_path, problem_path)
    file_name = ProblemOrganizer.get_exact_same_problem(domain_path,
                                                        problem_path,
                                                        metadata_obj)
    if file_name is None:
        file_name = data_helper.domain_name \
                    + ProblemOrganizer.goals_hash(data_helper.goals)

    if to_fork:
        ql_pid = os.fork()

        if ql_pid == 0:
            learner = qlearning.BackwardQLearning(file_name)
            local_simulator.LocalSimulator().run(domain_path, problem_path, learner)
            sys.exit(0)
        elif ql_pid < 0:
            print "error - can't fork to run q learning"

        mcts_learner = mcts.MonteCarloTreeSearch(file_name)
        local_simulator.LocalSimulator().run(domain_path, problem_path,
                                             mcts_learner)
        dom_name = data_helper.domain_name
        new_tuple = data_helper.problem_name, problem_path, data_helper.goals
        if dom_name in metadata_obj:
            metadata_obj = add_to_metadata(new_tuple, dom_name, metadata_obj)
        else:
            metadata_obj[dom_name] = [new_tuple]

        io_handler.IOHandler.write(metadata_f_name, metadata_obj)
    else:
        while True:
            learner = qlearning.BackwardQLearning(file_name, True)
            local_simulator.LocalSimulator().run(domain_path, problem_path,
                                                 learner)
            if learner.success_counter >= success_threshold:
                break
        return file_name


# PATCH: This only uses BQL now, instead of being a portfolio of MCTS and BQL.
def handle_known_problem(file_name):
    """
    function to handle a know problem. that is a problem that agent has plan for.
    :param file_name: prefix of file name
    """

    executive = qlearning.QLearningExecutive(file_name)
        
    if executive.get_plan() is None:
        handle_unknown_problem()
        return

    local_simulator.LocalSimulator().run(domain_path, problem_path,
                                         executive)


def handle_unknown_problem():
    """
    method handling state where a new problem arrived and no learning was made.
    if problem is deterministic, use plan_dispatch.
    o.w. learn for 2 minutes and than execute problem.
    """
    plan = try_planner()
    if plan:
        executive = ProblemOrganizer(domain_path, problem_path, plan)
        local_simulator.LocalSimulator().run(domain_path, problem_path,
                                             executive)
    else:
        file_name = learn(meta_data_object, False)
        executive = qlearning.QLearningExecutive(file_name)
        local_simulator.LocalSimulator().run(domain_path, problem_path,
                                             executive)


def execute(file_name):
    """
    method for execution phase.
    distinguish between learned and unlearned problems.
    if learned - run the faster executive.
    o.w - call helper function for unhandled problem.
    :param file_name: name of file. if is None => unknown problem
    """

    if file_name is not None:
        handle_known_problem(file_name)
    else:
        handle_unknown_problem()


flag = sys.argv[1]
domain_path = sys.argv[2]
problem_path = sys.argv[3]


if domain_path and problem_path:
    meta_data_object = io_handler.IOHandler.read(metadata_f_name)
    if meta_data_object is None:
        meta_data_object = {}

    if flag == "-L":
        learn(meta_data_object, to_fork=False)
    elif flag == "-E":
        prefix = ProblemOrganizer.get_similar_problem_file_name(domain_path, problem_path,
                                                                meta_data_object)
        execute(prefix)
    else:
        print "Illegal flag. Program Expect '-L'/ '-E' for learning/ executing"
else:
    print "Illegal input"
