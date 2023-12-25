import hashlib
from pddlsim.parser_independent import ProbabilisticAction


def flat_goals(goals):
    return [part for goal in goals for part in goal.parts]


def is_deterministic_domain(services):
    actions = services.parser.actions.items()
    for action_tpl in actions:
        action = action_tpl[1]
        if isinstance(action, ProbabilisticAction):
            return False

    return True


def get_action_prob_ratio(services, action_string):
    action_name = services.parser.parse_action(action_string)[0]
    action = services.parser.actions[action_name]
    if not hasattr(action, "prob_list"):
        ratio = 0
    else:
        probs = action.prob_list
        ratio = round(min(probs) / max(probs), 3) * 2

    return ratio


def state_to_hash(state):
    if state is None:
        return None

    # sort state for injective identification
    sorted_state = {}
    for predicate in state:
        val = list(state[predicate])
        if len(val) > 0:
            sorted_state[predicate] = sorted(val, key=lambda x: x)

    sorted_state = sorted(sorted_state.items())
    state_string = repr(sorted_state)
    return hashlib.sha1(state_string).hexdigest()
