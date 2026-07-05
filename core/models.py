from dataclasses import dataclass, field


@dataclass
class Task:

    user_request: str

    goal: str = ""

    task_type: str = ""

    expected_output: str = "answer"

    search_queries: list = field(default_factory=list)

    visited_urls: set = field(default_factory=set)

    documents: list = field(default_factory=list)

    results: list = field(default_factory=list)

    target_count: int = 0

    current_count: int = 0

    status: str = "planning"

    completed: bool = False