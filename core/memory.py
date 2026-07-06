import json
from pathlib import Path


class Memory:

    def __init__(self):

        self.memory_dir = Path("memory")
        self.memory_dir.mkdir(exist_ok=True)

    def save(self, task):

        filename = (
            task.goal.lower()
            .replace(" ", "_")
            .replace("/", "_")
        )[:80]

        path = self.memory_dir / f"{filename}.json"

        data = {
            "goal": task.goal,
            "summary": task.final_answer,
            "facts": task.extracted_data,
            "thoughts": task.thoughts,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_all(self):

        memories = []

        for file in self.memory_dir.glob("*.json"):

            try:

                with open(file, "r", encoding="utf-8") as f:
                    memories.append(json.load(f))

            except Exception:
                pass

        return memories


memory = Memory()