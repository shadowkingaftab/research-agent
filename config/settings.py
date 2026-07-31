import os
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Settings:
    # Workspace & Persistence
    workspace_dir: str = os.getenv("RESEARCH_OS_WORKSPACE", "./workspace")
    max_recursion_depth: int = int(os.getenv("RESEARCH_OS_MAX_DEPTH", 3))
    
    # Execution Limits
    max_steps_per_subgoal: int = int(os.getenv("RESEARCH_OS_MAX_STEPS_SUBGOAL", 15))
    global_max_steps: int = int(os.getenv("RESEARCH_OS_GLOBAL_MAX_STEPS", 60))
    evidence_sufficiency_threshold: float = float(os.getenv("RESEARCH_OS_EVIDENCE_THRESHOLD", 0.85))
    
    # LLM & Models
    llm_model: str = os.getenv("RESEARCH_OS_LLM_MODEL", "gpt-4o")
    llm_temperature: float = float(os.getenv("RESEARCH_OS_LLM_TEMP", 0.2))
    
    # Features
    enable_telemetry: bool = os.getenv("RESEARCH_OS_TELEMETRY", "true").lower() == "true"
    enable_learning: bool = os.getenv("RESEARCH_OS_LEARNING", "true").lower() == "true"
    enable_memory: bool = os.getenv("RESEARCH_OS_MEMORY", "true").lower() == "true"
    
    # Search & Retrieval
    search_results_limit: int = int(os.getenv("RESEARCH_OS_SEARCH_LIMIT", 10))
    crawl_depth: int = int(os.getenv("RESEARCH_OS_CRAWL_DEPTH", 1))
    
    # Plugin & Extension Paths
    plugin_dirs: List[str] = field(default_factory=lambda: ["./tools", "./agents"])

    def validate(self):
        if self.max_recursion_depth < 1:
            raise ValueError("max_recursion_depth must be at least 1")
        if self.evidence_sufficiency_threshold < 0 or self.evidence_sufficiency_threshold > 1:
            raise ValueError("evidence_sufficiency_threshold must be between 0 and 1")

settings = Settings()
settings.validate()