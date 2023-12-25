"""
A copy of valid_actions class but with a possibility to get valid actions by a given state
"""


def get_valid_actions(services, state=None):
    if state == None:
        state = services.perception.get_state()
    possible_actions = []
    for name, action in services.parser.actions.items():
        for candidate in get_valid_candidates_for_action(state, action):
            possible_actions.append(action.action_string(candidate))
    return possible_actions


def join_candidates(previous_candidates, new_candidates, p_indexes, n_indexes):
    shared_indexes = p_indexes.intersection(n_indexes)
    if previous_candidates is None:
        return new_candidates
    result = []
    for c1 in previous_candidates:
        for c2 in new_candidates:
            if all([c1[idx] == c2[idx] for idx in shared_indexes]):
                merged = c1[:]
                for idx in n_indexes:
                    merged[idx] = c2[idx]
                result.append(merged)
    return result


def indexed_candidate_to_dict(candidate, index_to_name):
    return {name[0]: candidate[idx] for idx, name in index_to_name.items()}


def get_valid_candidates_for_action(state, action):
    """
    Get all the valid parameters for a given action for the current state of the simulation
    """
    objects = dict()
    signatures_to_match = {
        name: (idx, t) for idx, (name, t) in enumerate(action.signature)
    }
    index_to_name = {idx: name for idx, name in enumerate(action.signature)}
    candidate_length = len(signatures_to_match)
    found = set()
    candidates = None
    # copy all preconditions
    for precondition in sorted(action.precondition, key=lambda x: len(state[x.name])):
        thruths = state[precondition.name]
        if len(thruths) == 0:
            return []
        # map from predicate index to candidate index
        dtypes = [(name, "object") for name in precondition.signature]
        reverse_map = {
            idx: signatures_to_match[pred][0]
            for idx, pred in enumerate(precondition.signature)
        }
        indexes = reverse_map.values()
        overlap = len(found.intersection(indexes)) > 0
        precondition_candidates = []
        for entry in thruths:
            candidate = [None] * candidate_length
            for idx, param in enumerate(entry):
                candidate[reverse_map[idx]] = param
            precondition_candidates.append(candidate)

        candidates = join_candidates(
            candidates, precondition_candidates, found, indexes
        )
        found = found.union(indexes)

    return [indexed_candidate_to_dict(c, index_to_name) for c in candidates]
