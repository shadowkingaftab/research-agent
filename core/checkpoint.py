import os
import json
import time
from typing import Dict, Any, List
from datetime import datetime
from core.logger import logger

class CheckpointManager:
    def __init__(self, base_dir: str = "./workspace/checkpoints"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def save(self, project_id: str, task_state: Dict[str, Any], stage: str = "generic"):
        timestamp = int(datetime.utcnow().timestamp())
        filename = f"{project_id}_{stage}_{timestamp}.json"
        filepath = os.path.join(self.base_dir, filename)
        
        # Serialize only JSON-compatible parts of the task
        safe_state = {
            "goal": task_state.get("goal"),
            "current_step": task_state.get("current_step"),
            "sub_goal_index": task_state.get("current_sub_goal_index"),
            "extracted_data_count": len(task_state.get("extracted_data", [])),
            "documents_count": len(task_state.get("documents", [])),
            "final_answer": task_state.get("final_answer"),
            "timestamp": timestamp
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(safe_state, f, indent=2)
            logger.log(f"Checkpoint saved: {filename}")
        except Exception as e:
            logger.log(f"Checkpoint save failed: {e}")

    def load_latest(self, project_id: str) -> Dict[str, Any]:
        checkpoints = [f for f in os.listdir(self.base_dir) if f.startswith(project_id)]
        if not checkpoints:
            return {}
        
        latest = sorted(checkpoints)[-1]
        filepath = os.path.join(self.base_dir, latest)
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.log(f"Checkpoint load failed: {e}")
            return {}

    def rollback(self, project_id: str, steps_back: int = 1):
        checkpoints = sorted([f for f in os.listdir(self.base_dir) if f.startswith(project_id)])
        if len(checkpoints) <= steps_back:
            logger.log("No earlier checkpoints available for rollback.")
            return None
        
        target = checkpoints[-(steps_back + 1)]
        filepath = os.path.join(self.base_dir, target)
        logger.log(f"Rolling back to checkpoint: {target}")
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.log(f"Rollback failed: {e}")
            return None

checkpoint_manager = CheckpointManager()