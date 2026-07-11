import json
from pathlib import Path
from dataclasses import asdict

from models.evidence import Evidence


class ResearchMemory:

    def __init__(self):

        self.memory_dir = Path("memory")
        self.memory_dir.mkdir(exist_ok=True)

    def _project_file(self, project_name: str):

        filename = (
            project_name.lower()
            .replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
        )

        return self.memory_dir / f"{filename}.json"

    def save(self, project_name: str, evidence_list):

        path = self._project_file(project_name)

        serializable = []

        for item in evidence_list:

            try:
                serializable.append(asdict(item))
            except Exception:
                serializable.append(item)

        with open(path, "w", encoding="utf-8") as f:

            json.dump(
                serializable,
                f,
                indent=2,
                ensure_ascii=False,
            )

    def load(self, project_name: str):

        path = self._project_file(project_name)

        if not path.exists():
            return []

        with open(path, "r", encoding="utf-8") as f:

            data = json.load(f)

        evidence = []

        for item in data:

            try:
                evidence.append(Evidence(**item))
            except Exception:
                continue

        return evidence

    def search(self, project_name: str, query: str):

        results = []

        for item in self.load(project_name):

            text = " ".join(
                [
                    item.fact,
                    item.summary,
                    " ".join(item.entities),
                    " ".join(item.keywords),
                ]
            ).lower()

            if query.lower() in text:

                results.append(item)

        return results

    def clear(self, project_name: str):

        path = self._project_file(project_name)

        if path.exists():
            path.unlink()


research_memory = ResearchMemory()