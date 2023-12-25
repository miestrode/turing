from os import path, makedirs
import json
from utils.knowledge_graph import KnowldegeGraph

"""
 A utility for loading and saving files (policies, knowledge, learning_params)
"""

policies_folder = "./data/policies"
knowledge_folder = "./data/knowledge"
learning_params_folder = "./data/learning_params"

policy_key = "policy"
goal_key = "goal"
effects_ratio_key = "effects_ratio"
q_table_key = "q_table"
age_key = "age"
exploration_rate_key = "exploration_rate"
learning_rate_key = "learning_rate"
graph_key = "graph"

policy_file_prefix = "policy_"
knowledge_file_prefix = "knowledge_"
params_file_prefix = "params_"
file_extention = ".json"


def get_policy_file_path(services, create_if_not_exists=False):
    if create_if_not_exists and not path.exists(policies_folder):
        makedirs(policies_folder)

    return path.join(
        policies_folder,
        policy_file_prefix + services.parser.problem_name + file_extention,
    )


def get_knowledge_file_path(services, create_if_not_exists=False):
    if create_if_not_exists and not path.exists(knowledge_folder):
        makedirs(knowledge_folder)

    return path.join(
        knowledge_folder,
        knowledge_file_prefix + services.parser.domain_name + file_extention,
    )


def get_learning_params_file_path(services, create_if_not_exists=False):
    if create_if_not_exists and not path.exists(learning_params_folder):
        makedirs(learning_params_folder)

    return path.join(
        learning_params_folder,
        params_file_prefix + services.parser.problem_name + file_extention,
    )


def load_knowledge_graph(services):
    knowledge_file = get_knowledge_file_path(services)

    if not path.exists(knowledge_file):
        raise IOError()

    with open(knowledge_file) as json_file:
        content = json.load(json_file)
        graph = content.get(graph_key)
        knowledge_graph = KnowldegeGraph(services, graph)

    return knowledge_graph


def load_learning_params_file(services):
    learning_params_file = get_learning_params_file_path(services)

    if not path.exists(learning_params_file):
        raise IOError()

    with open(learning_params_file) as json_file:
        content = json.load(json_file)
        q_table = content.get(q_table_key)
        starting_step = content.get(age_key)
        exploration_rate = content.get(exploration_rate_key)
        learning_rate = content.get(learning_rate_key)

    return q_table, starting_step, exploration_rate, learning_rate


def load_policy_file(services, with_effects_ratio=False):
    policy_file = get_policy_file_path(services)

    if not path.exists(policy_file):
        raise IOError()

    with open(policy_file) as json_file:
        content = json.load(json_file)
        policy = content[policy_key]
        goal = content[goal_key]
        if with_effects_ratio:
            effects_ratio = content[effects_ratio_key]

    if with_effects_ratio:
        return policy, goal, effects_ratio
    return policy, goal


def save_policy(services, policy, goal, effects_ratio):
    policy_file = get_policy_file_path(services, True)

    try:
        current_policy, current_goal, current_ratio = load_policy_file(services, True)
        if (
            policy != None
            and len(current_policy) <= len(policy)
            and current_ratio <= effects_ratio
        ):
            return
        if policy == None:
            # In case goal or effect_ratio changed
            policy = current_policy
    except IOError:
        pass

    with open(policy_file, "w") as outfile:
        content = {}
        content[policy_key] = policy
        content[goal_key] = goal
        content[effects_ratio_key] = effects_ratio

        json.dump(content, outfile)


def save_knowledge(services, graph_json):
    knowledge_file = get_knowledge_file_path(services, True)

    with open(knowledge_file, "w") as outfile:
        content = {}
        content[graph_key] = graph_json

        json.dump(content, outfile)


def save_learning_params(services, q_table, age, exploration_rate, learning_rate):
    learning_params_file = get_learning_params_file_path(services, True)

    with open(learning_params_file, "w") as outfile:
        content = {}
        content[q_table_key] = q_table
        content[age_key] = age
        content[exploration_rate_key] = exploration_rate
        content[learning_rate_key] = learning_rate

        json.dump(content, outfile)
