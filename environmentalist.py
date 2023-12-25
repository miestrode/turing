import glob
import os
import re

PROBLEM = re.compile(r"\(\s*problem\s+[a-zA-Z_][a-zA-Z-0-9_]*\s*\)")


def main():
    for file_path in glob.glob("./**/*.pddl") + glob.glob("./*.pddl"):
        if os.path.basename(file_path) != "domain.pddl":
            with open(file_path, "r") as file:
                contents = file.read()
                print(contents)

            with open(file_path, "w") as file:
                file.write(
                    contents.replace(
                        PROBLEM.findall(contents)[0], f"(problem {os.path.basename(file_path).split('.')[0]})"
                    )
                )


if __name__ == "__main__":
    main()
