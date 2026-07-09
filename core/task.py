from dataclasses import dataclass, field


@dataclass
class Task:
    # -------------------------
    # User Input
    # -------------------------

    user_request: str

    # -------------------------
    # Planner Output
    # -------------------------

    goal: str = ""
    task_type: str = ""
    expected_output: str = ""

    search_queries: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)

    # -------------------------
    # Search Stage
    # -------------------------

    search_results: list = field(default_factory=list)
    visited_urls: set = field(default_factory=set)

    # -------------------------
    # Crawl Stage
    # -------------------------

    documents: list = field(default_factory=list)
    research_corpus: str = ""

    # -------------------------
    # Extraction Stage
    # -------------------------

    extracted_data: list = field(default_factory=list)
    retrieved_evidence: list = field(default_factory=list)

    # -------------------------
    # Agent State
    # -------------------------

    thoughts: list = field(default_factory=list)
    action_history: list = field(default_factory=list)
    current_step: int = 0

    # -------------------------
    # Memory
    # -------------------------

    previous_memories: list = field(default_factory=list)

    # -------------------------
    # Final Output
    # -------------------------

    final_answer: str = ""

    # -------------------------
    # Shared Data Between Tools
    # -------------------------

    data: dict = field(default_factory=dict)

    # -------------------------
    # Status
    # -------------------------

    status: str = "created"