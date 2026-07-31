import os
import json
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, Any
from datetime import datetime
from core.logger import logger

@dataclass
class ResearchProject:
    id: str
    name: str
    status: str  # "active", "completed", "paused"
    created_at: str
    updated_at: str
    context_state: Dict[str, Any] = field(default_factory=dict)
    report_versions: list = field(default_factory=list)

class Workspace:
    def __init__(self, base_dir: str = "./workspace"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        self.active_projects: Dict[str, ResearchProject] = self._load_projects()

    def _load_projects(self) -> Dict[str, ResearchProject]:
        projects = {}
        meta_file = os.path.join(self.base_dir, "projects.json")
        if os.path.exists(meta_file):
            try:
                with open(meta_file, 'r') as f:
                    data = json.load(f)
                    for pid, p_data in data.items():
                        projects[pid] = ResearchProject(**p_data)
            except Exception as e:
                logger.log(f"Warning: Failed to load workspace metadata: {e}")
        return projects

    def create_project(self, name: str) -> ResearchProject:
        pid = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        project = ResearchProject(id=pid, name=name, status="active", created_at=now, updated_at=now)
        self.active_projects[pid] = project
        self._save_projects()
        logger.log(f"Workspace: Created project '{name}' [{pid}]")
        return project

    def get_project(self, project_id: str) -> ResearchProject:
        if project_id not in self.active_projects:
            raise ValueError(f"Project {project_id} not found in workspace.")
        return self.active_projects[project_id]

    def save_checkpoint(self, project_id: str, context_state: Dict[str, Any]):
        project = self.get_project(project_id)
        project.context_state = context_state
        project.updated_at = datetime.utcnow().isoformat()
        self._save_projects()
        
        checkpoint_dir = os.path.join(self.base_dir, project_id, "checkpoints")
        os.makedirs(checkpoint_dir, exist_ok=True)
        checkpoint_file = os.path.join(checkpoint_dir, f"state_{int(datetime.utcnow().timestamp())}.json")
        with open(checkpoint_file, 'w') as f:
            json.dump(context_state, f, indent=2)

    def _save_projects(self):
        meta_file = os.path.join(self.base_dir, "projects.json")
        with open(meta_file, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.active_projects.items()}, f, indent=2)

workspace = Workspace()