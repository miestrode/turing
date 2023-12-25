class Converter:
    """
    Converter - Converts a probabilistic domain to a deterministic domain.
    """

    # Constructor
    def __init__(self, domain_path):
        self.domain_path = domain_path
        self.new_domain_path = None

    def convert_to_deterministic_high_prob(self):
        in_action = False
        in_effect = False
        in_prob = False
        effect_finished = True
        self.new_domain_path = self.domain_path.replace(".pddl", "") + "_new_high.pddl"
        self.converted_to_deterministic = True
        with open(self.domain_path, "r") as origin_domain, open(
            self.new_domain_path, "w"
        ) as new_domain:
            for line in origin_domain:
                if line[0] == ";":
                    new_domain.write(line)
                    continue
                if "action" in line:
                    action_open_parenthesis = 0
                    action_close_parenthesis = 0
                    action_info = ""
                    in_action = True
                    effect_finished = False
                    effects_list = []
                if in_action or not effect_finished:
                    action_open_parenthesis += line.count("(")
                    action_close_parenthesis += line.count(")")
                    action_info += line
                    if action_open_parenthesis <= action_close_parenthesis:
                        in_action = False
                    if "effect" in line:
                        effect_open_parenthesis = 0
                        effect_close_parenthesis = 0
                        effect_info = ""
                        in_effect = True
                    if in_effect:
                        effect_open_parenthesis += line.count("(")
                        effect_close_parenthesis += line.count(")")
                        effect_info += line
                        if 0 < effect_open_parenthesis <= effect_close_parenthesis:
                            in_effect = False
                            if effect_open_parenthesis == 2:
                                index = effect_info.find("(", effect_info.find("(") + 1)
                                effect = effect_info[index:]
                                effects_list.append(effect)
                            elif "probabilistic" in effect_info:
                                prob_open_parenthesis = 0
                                prob_close_parenthesis = 0
                                splits = effect_info.split(" ")
                                last_split = None
                                max_prob = 0
                                for split in splits:
                                    if split == "and" or split == "(and":
                                        in_prob = True
                                        prob = float(last_split)
                                        effect = ""
                                    if in_prob:
                                        prob_open_parenthesis += split.count("(")
                                        prob_close_parenthesis += split.count(")")
                                        effect += split + " "
                                        if (
                                            prob_open_parenthesis
                                            <= prob_close_parenthesis
                                        ):
                                            in_prob = False
                                            if prob == max_prob:
                                                effect = effect[:-1]
                                                effects_list.append(effect)
                                            if prob > max_prob:
                                                max_prob = prob
                                                effect = effect[:-1]
                                                effects_list = [effect]
                                    last_split = split
                            else:
                                splits = effect_info.split()
                                add_to_effect = False
                                effect = ""
                                for split in splits:
                                    if split == "and" or split == "(and":
                                        add_to_effect = True
                                    if add_to_effect:
                                        effect += split + " "
                                effect = effect.replace(") )", "))")
                                effects_list.append(effect)
                            action_lines = action_info.splitlines()
                            effects_list_len = len(effects_list)
                            for i in range(effects_list_len):
                                new_action = ""
                                effect_part = False
                                for l in action_lines:
                                    if "effect" in l:
                                        effect_part = True
                                        effect_open_par = 0
                                        effect_close_par = 0
                                    if effect_part:
                                        effect_open_par += l.count("(")
                                        effect_close_par += l.count(")")
                                        if 0 < effect_open_par <= effect_close_par:
                                            effect_part = False
                                            new_action += (
                                                "\t :effect\n\t\t" + effects_list.pop(0)
                                            )
                                    elif "action" in l:
                                        action_name = l.split("action ", 1)[1]
                                        l = l.replace(
                                            action_name,
                                            action_name.replace(" ", "")
                                            + "_"
                                            + str(i + 1),
                                        )
                                        new_action += l + "\n"
                                    else:
                                        new_action += l + "\n"
                                if i < effects_list_len - 1:
                                    new_action += ")"
                                missing_par = new_action.count("(") - new_action.count(
                                    ")"
                                )
                                for j in range(missing_par):
                                    new_action += ")"
                                new_action += "\n"
                                new_domain.write(new_action)
                            effect_finished = True
                else:
                    new_domain.write(line)

    """
    def convert_to_deterministic_all_prob(self):
        in_action = False
        in_effect = False
        in_prob = False
        effect_finished = True
        self.new_domain_path = self.domain_path.replace('.pddl', '') + '_new.pddl'
        with open(self.domain_path, "r") as origin_domain, open(self.new_domain_path, "w") as new_domain:
            for line in origin_domain:
                if line[0] == ";":
                    new_domain.write(line)
                    continue
                if "action" in line:
                    action_open_parenthesis = 0
                    action_close_parenthesis = 0
                    action_info = ""
                    in_action = True
                    effect_finished = False
                    effects_list = []
                if in_action or not effect_finished:
                    action_open_parenthesis += line.count('(')
                    action_close_parenthesis += line.count(')')
                    action_info += line
                    if action_open_parenthesis <= action_close_parenthesis:
                        in_action = False
                    if "effect" in line:
                        effect_open_parenthesis = 0
                        effect_close_parenthesis = 0
                        effect_info = ""
                        in_effect = True
                    if in_effect:
                        effect_open_parenthesis += line.count('(')
                        effect_close_parenthesis += line.count(')')
                        effect_info += line
                        if 0 < effect_open_parenthesis <= effect_close_parenthesis:
                            in_effect = False
                            if effect_open_parenthesis == 2:
                                index = effect_info.find("(", effect_info.find("(") + 1)
                                effect = effect_info[index:]
                                effects_list.append(effect)
                            elif "probabilistic" in effect_info:
                                prob_open_parenthesis = 0
                                prob_close_parenthesis = 0
                                splits = effect_info.split(' ')
                                for split in splits:
                                    if split == "and" or split == "(and":
                                        in_prob = True
                                        effect = ""
                                    if in_prob:
                                        prob_open_parenthesis += split.count('(')
                                        prob_close_parenthesis += split.count(')')
                                        effect += split + ' '
                                        if prob_open_parenthesis <= prob_close_parenthesis:
                                            in_prob = False
                                            effect = effect[:-1]
                                            effects_list.append(effect)
                            else:
                                splits = effect_info.split()
                                add_to_effect = False
                                effect = ""
                                for split in splits:
                                    if split == "and" or split == "(and":
                                        add_to_effect = True
                                    if add_to_effect:
                                        effect += split + ' '
                                effect = effect.replace(") )", "))")
                                effects_list.append(effect)
                            action_lines = action_info.splitlines()
                            effects_list_len = len(effects_list)
                            for i in range(effects_list_len):
                                new_action = ""
                                effect_part = False
                                for l in action_lines:
                                    if "effect" in l:
                                        effect_part = True
                                        effect_open_par = 0
                                        effect_close_par = 0
                                    if effect_part:
                                        effect_open_par += l.count('(')
                                        effect_close_par += l.count(')')
                                        if 0 < effect_open_par <= effect_close_par:
                                            effect_part = False
                                            new_action += "\t :effect\n\t\t" + effects_list.pop(0)
                                    elif "action" in l:
                                        action_name = l.split("action ", 1)[1]
                                        l = l.replace(action_name, action_name.replace(" ", "") + "_" + str(i + 1))
                                        new_action += l + "\n"
                                    else:
                                        new_action += l + "\n"
                                if i < effects_list_len - 1:
                                    new_action += ")"
                                missing_par = new_action.count("(") - new_action.count(")")
                                for j in range(missing_par):
                                    new_action += ")"
                                new_action += "\n"
                                new_domain.write(new_action)
                            effect_finished = True
                else:
                    new_domain.write(line)
    """
