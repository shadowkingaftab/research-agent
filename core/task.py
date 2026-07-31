from dataclasses import dataclass, field
from typing import Any
from core.search_strategy import SearchStrategyState
@dataclass
class Task:
    # -------------------------
    # User Input
    # -------------------------
    user_request: str

    # -------------------------
    # Planner Output (Hierarchical)
    # -------------------------
    goal: str = ""
    task_type: str = ""
    expected_output: str = ""
    evidence_sufficiency_threshold: float = 0.85
    
    sub_goals: list[dict] = field(default_factory=list)
    current_sub_goal_index: int = 0
    
    search_queries: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)

    # -------------------------
    # Search & Crawl Stage
    # -------------------------
    search_results: list = field(default_factory=list)
    visited_urls: set = field(default_factory=set)
    documents: list = field(default_factory=list)
    research_corpus: str = ""

    # -------------------------
    # Extraction & Reasoning Stage
    # -------------------------
    extracted_data: list = field(default_factory=list)
    retrieved_evidence: list = field(default_factory=list)
    thoughts: list = field(default_factory=list)
    action_history: list = field(default_factory=list)
    current_step: int = 0
    
    recursion_depth: int = 0
    max_recursion_depth: int = 3
    is_evidence_sufficient: bool = False

    # -------------------------
    # Memory & Statistics
    # -------------------------
    research_statistics: dict = field(default_factory=dict)
    project_name: str = ""
    use_memory: bool = True
    loaded_memory: list = field(default_factory=list)
    memory_hits: int = 0

    # -------------------------
    # Shared Data & Status
    # -------------------------
    data: dict = field(default_factory=dict)
    status: str = "created"
    final_answer: str = ""
    strategy_state: Any = field(default=None) # Initialized as SearchStrategyState during execution