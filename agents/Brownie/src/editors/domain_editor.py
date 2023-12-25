import os

from pddlsim.fd_parser import FDParser
from pddlsim.parser_independent import Action, ProbabilisticAction

from src.handlers.probabilities_learning_handler import ActionProbabilitiesUtils


class DomainEditor:
    DETERMINISTIC_DOMAIN_DIRECTORY = "deterministic_domains"
    REVEAL_DOMAIN_DIRECTORY = "reveal_domains"

    def __init__(self):
        pass

    @staticmethod
    def get_action_name_from_custom_action(custom_action):
        return custom_action.rsplit("_", 1)[0]

    @staticmethod
    def get_action_signature_from_custom_action_signature(custom_action_signature):
        custom_action_name, parameters = custom_action_signature.split(" ", 1)
        action_name = DomainEditor.get_action_name_from_custom_action(
            custom_action_name
        )

        return " ".join([action_name, parameters])

    @staticmethod
    def get_action_name_of_probabilistic_action(probabilistic_action, i):
        return "{}_{}".format(probabilistic_action.name, i)

    @staticmethod
    def convert_probabilistic_action_to_action(probabilistic_action, i):
        if isinstance(probabilistic_action, Action):
            return probabilistic_action

        name = DomainEditor.get_action_name_of_probabilistic_action(
            probabilistic_action, i
        )
        signature = probabilistic_action.signature
        addlist = probabilistic_action.addlists[i]
        dellist = probabilistic_action.dellists[i]
        precondition = probabilistic_action.precondition

        return Action(name, signature, addlist, dellist, precondition)

    @staticmethod
    def get_reveal_domain_path(domain_name):
        return "{}/{}".format(DomainEditor.REVEAL_DOMAIN_DIRECTORY, domain_name)

    @staticmethod
    def get_deterministic_domain_path(domain_name):
        return "{}/{}".format(DomainEditor.DETERMINISTIC_DOMAIN_DIRECTORY, domain_name)

    @staticmethod
    def write_pddl_domain_file(parser, dellist=True):
        domain_name = parser.domain_name

        if dellist:
            domain_path = DomainEditor.get_deterministic_domain_path(domain_name)
        else:
            domain_path = DomainEditor.get_reveal_domain_path(domain_name)

        directory_path = domain_path.rsplit("/", 1)[0]

        if not os.path.isdir(directory_path):
            os.mkdir(directory_path)

        with open(domain_path, "w") as f:
            f.write("(define (domain {})\n".format(domain_name))

            f.write("\t" + "(:predicates\n")
            f.write("\t" * 2)
            for predicate in parser.task.predicates:
                if not predicate.name == "=":
                    name = predicate.name
                    arguments_name = [argument.name for argument in predicate.arguments]
                    arguments_name.insert(0, name)

                    predicate_string = " ".join(arguments_name)

                    f.write("({}) ".format(predicate_string))
            f.write("\n\t)\n\n")

            for action in parser.actions.values():
                if isinstance(action, Action):
                    f.write("\t(:action {}\n".format(action.name))

                    parameters = [item[0] for item in action.signature]
                    parameters_string = " ".join(parameters)
                    f.write("\t :parameters ( {})\n".format(parameters_string))

                    f.write("\t :precondition\n")
                    f.write("\t" * 2 + "(and ")

                    for precondition in action.precondition:
                        signature = list(precondition.signature)
                        signature.insert(0, precondition.name)
                        precondition_string = " ".join(signature)
                        f.write("({}) ".format(precondition_string))

                    f.write(")\n\t :effect\n")
                    f.write("\t\t(and ")

                    for add_item in action.addlist:
                        signature = list(add_item[1])
                        signature.insert(0, add_item[0])
                        add_item_string = " ".join(signature)
                        f.write("({}) ".format(add_item_string))

                    if dellist:
                        for del_item in action.dellist:
                            f.write("(not ")
                            signature = list(del_item[1])
                            signature.insert(0, del_item[0])
                            del_item_string = " ".join(signature)
                            f.write("({})) ".format(del_item_string))

                    f.write(")\n")
                f.write("\t)\n")

            f.write(")")

    @staticmethod
    def write_deterministic_domain_from_stochastic_domain(parser, dellist=True):
        custom_parser = FDParser(parser.domain_path, parser.problem_path)

        deterministic_actions = {}

        for action in custom_parser.actions.values():
            if isinstance(action, Action):
                action_name = DomainEditor.get_action_name_of_probabilistic_action(
                    action, 0
                )
                action.name = action_name
                deterministic_actions[action_name] = action
            elif isinstance(action, ProbabilisticAction):
                for effect_index in range(len(action.prob_list)):
                    deterministic_action = (
                        DomainEditor.convert_probabilistic_action_to_action(
                            action, effect_index
                        )
                    )
                    if (
                        len(deterministic_action.addlist) > 0
                        or len(deterministic_action.dellist) > 0
                    ):
                        deterministic_actions[
                            deterministic_action.name
                        ] = deterministic_action

        custom_parser.actions = deterministic_actions

        DomainEditor.write_pddl_domain_file(custom_parser, dellist)

    @staticmethod
    def write_filtered_effects_deterministic_domain_from_stochastic_domain(
        parser, actions_probabilities, min_probability=0.1
    ):
        custom_parser = FDParser(parser.domain_path, parser.problem_path)
        filtered_effects_actions = {}

        for action in custom_parser.actions.values():
            if isinstance(action, Action):
                action_name = DomainEditor.get_action_name_of_probabilistic_action(
                    action, 0
                )
                action.name = action_name
                filtered_effects_actions[action_name] = action
            elif isinstance(action, ProbabilisticAction):
                for effect_index in range(len(action.prob_list)):
                    if (
                        ActionProbabilitiesUtils.get_probability(
                            actions_probabilities[action.name], effect_index
                        )
                        >= min_probability
                    ):
                        deterministic_action = (
                            DomainEditor.convert_probabilistic_action_to_action(
                                action, effect_index
                            )
                        )
                        if len(deterministic_action.addlist) > 0:
                            filtered_effects_actions[
                                deterministic_action.name
                            ] = deterministic_action

        custom_parser.actions = filtered_effects_actions

        DomainEditor.write_pddl_domain_file(custom_parser)
