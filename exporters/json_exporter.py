import json
from dataclasses import asdict, is_dataclass

from exporters.base import Exporter


class JSONExporter(Exporter):

    def _serialize(self, value):

        if is_dataclass(value) and not isinstance(value, type):
            return asdict(value)

        if isinstance(value, list):
            return [self._serialize(v) for v in value]

        if isinstance(value, dict):
            return {k: self._serialize(v) for k, v in value.items()}

        return value

    def export(self, title, task):

        filename = self.safe_filename(title) + ".json"

        path = self.output_dir / filename

        data = {
            "goal": task.goal,
            "user_request": task.user_request,
            "final_answer": task.final_answer,
            "evidence": self._serialize(task.extracted_data),
            "retrieved_evidence": self._serialize(task.retrieved_evidence),
            "research_statistics": task.research_statistics,
            "knowledge_graph": task.data.get("knowledge_graph", {}),
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return path