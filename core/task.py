from dataclasses import dataclass, field


@dataclass
class Task:

    # Original user request
    user_request: str

    # Planner output
    goal: str = ""
    task_type: str = ""
    expected_output: str = ""

    # Workflow
    search_queries: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)

    # Search stage
    search_results: list = field(default_factory=list)

    # Crawl stage
    documents: list = field(default_factory=list)

    research_corpus: str = ""

    # Extraction stage
    extracted_data: list = field(default_factory=list)

    # Final answer
    final_answer: str = ""

    # Keep track of visited pages
    visited_urls: set = field(default_factory=set)

    # Shared state for tools
    data: dict = field(default_factory=dict)

    # Status
    status: str = "created"
    
    thoughts: list = field(default_factory=list)
    action_history: list = field(default_factory=list)
    current_step: int = 0

    research_corpus: str = ""
    extracted_data: list = field(default_factory=list)
    search_results: list = field(default_factory=list)

    final_answer: str = ""