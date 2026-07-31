from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime

@dataclass
class AgentEvent:
    event_type: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PlanningStarted(AgentEvent):
    event_type: str = "PlanningStarted"
    query: str = ""

@dataclass
class PlanningCompleted(AgentEvent):
    event_type: str = "PlanningCompleted"
    sub_goal_count: int = 0
    tools_assigned: list = field(default_factory=list)

@dataclass
class SubGoalStarted(AgentEvent):
    event_type: str = "SubGoalStarted"
    sub_goal_index: int = 0
    description: str = ""

@dataclass
class ToolStarted(AgentEvent):
    event_type: str = "ToolStarted"
    tool_name: str = ""
    step: int = 0

@dataclass
class ToolCompleted(AgentEvent):
    event_type: str = "ToolCompleted"
    tool_name: str = ""
    duration_ms: float = 0.0
    evidence_delta: int = 0

@dataclass
class SearchCompleted(AgentEvent):
    event_type: str = "SearchCompleted"
    results_count: int = 0

@dataclass
class CrawlProgress(AgentEvent):
    event_type: str = "CrawlProgress"
    urls_visited: int = 0
    documents_extracted: int = 0

@dataclass
class ExtractionProgress(AgentEvent):
    event_type: str = "ExtractionProgress"
    new_facts: int = 0
    total_facts: int = 0

@dataclass
class MergeCompleted(AgentEvent):
    event_type: str = "MergeCompleted"
    corpus_size: int = 0

@dataclass
class RetrievalCompleted(AgentEvent):
    event_type: str = "RetrievalCompleted"
    retrieved_count: int = 0

@dataclass
class WriterStarted(AgentEvent):
    event_type: str = "WriterStarted"

@dataclass
class WriterCompleted(AgentEvent):
    event_type: str = "WriterCompleted"
    report_length: int = 0

@dataclass
class Finished(AgentEvent):
    event_type: str = "Finished"
    total_steps: int = 0
    final_confidence: float = 0.0

@dataclass
class Error(AgentEvent):
    event_type: str = "Error"
    message: str = ""
    tool_name: Optional[str] = None