import json
from pathlib import Path


class ProjectManager:

    def __init__(self):

        self.project_dir = Path("projects")
        self.project_dir.mkdir(exist_ok=True)

    def save(self, task):

        filename = (
            task.goal.lower()
            .replace(" ", "_")
            .replace("/", "_")
        )[:80]

        path = self.project_dir / f"{filename}.json"

        data = {
            "user_request": task.user_request,
            "goal": task.goal,
            "task_type": task.task_type,
            "expected_output": task.expected_output,
            "search_queries": task.search_queries,
            "documents": task.documents,
            "search_results": task.search_results,
            "research_corpus": task.research_corpus,
            "extracted_data": task.extracted_data,
            "final_answer": task.final_answer,
            "thoughts": getattr(task, "thoughts", []),
            "visited_urls": list(task.visited_urls),
            "data": task.data,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return path

    def load(self, filename):

        path = self.project_dir / filename

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_projects(self):

        return sorted(self.project_dir.glob("*.json"))


project_manager = ProjectManager()