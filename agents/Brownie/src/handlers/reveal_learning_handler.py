import json
import os


class RevealLearningHandler:
    def __init__(self, path):
        self.path = path

        if os.path.isfile(path):
            self.reveals = self.load_reveal_file()
        else:
            self.reveals = []

    def load_reveal_file(self):
        with open(self.path, "r") as f:
            return json.load(f)

    def save_reveal_file(self):
        with open(self.path, "w") as f:
            json.dump(self.reveals, f)

    def append(self, new_reveals):
        for reveal in new_reveals:
            if reveal not in self.reveals:
                self.reveals.append(reveal)

        self.save_reveal_file()
