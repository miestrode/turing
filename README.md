# Turing
Turing is a PDDLsim agent evaluator. Assuming you have a python environment running python 2 and PDDLsim, alongside a collection of agents in the `agents/` directory, you can evaluate these agents on the test problems set out in `domains/` (or replace them with your own problems, given they fit the format of the problems there).

## Usage
In order to evaluate agents A, B, C, D, ..., simply run:
```
python run.py A B C D ...
```

With Python 3.11. The `agents/` directory contains by default some agents, which were used for the research that this repository was meant to serve, although you can at any time delete the agents and replace them with your own. Simply do note each agent you use must have an entry point in `my_executive.py` (and have it's own folder, of course). Finally, note that you can edit the parameters of the `run.py` script to your liking, and that you should clean the `rundirs/` directory after finishing a run, even though it is automatically cleaned once you start a new run.

## Using your own problems
When using your own problems, simply put them in the `domains/` directory, in their own directory, which should have a domain in `domain.pddl` and a set of problems, whose filename must match their problem name. If your agents require the problem name contain an environment and task, these may have to include a `-`.

## Maintenance status
This project is currently not actively maintained, although feel free to file issues in the repository, which I will consider to fix depending on their severity. This repository is mainly used for research purposes.
