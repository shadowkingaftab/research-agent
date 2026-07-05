import json
from pathlib import Path


class ProjectManager:

    def __init__(self):

        self.base = Path("projects")
        self.base.mkdir(exist_ok=True)

    def save(self, name, task):

        folder = self.base / name
        folder.mkdir(exist_ok=True)

        with open(folder / "task.json", "w", encoding="utf-8") as f:
            json.dump(task.__dict__, f, indent=2, default=list)

    def load(self, name):

        folder = self.base / name

        with open(folder / "task.json", encoding="utf-8") as f:
            return json.load(f)


projects = ProjectManager()