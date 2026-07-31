import time
from typing import List, Dict, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from core.logger import logger

@dataclass
class TelemetryEvent:
    timestamp: str
    phase: str
    event_type: str
    details: Dict[str, Any]
    duration_ms: float = 0.0

class TelemetryTracker:
    def __init__(self):
        self.events: List[TelemetryEvent] = []
        self.start_time = time.time()
        self.total_tokens = 0
        self.estimated_cost = 0.0
        self.confidence_trajectory: List[float] = []
        self.tool_stats: Dict[str, Dict[str, Any]] = {}
        self.retrieval_metrics: List[Dict[str, float]] = []

    def record(self, phase: str, event_type: str, details: Dict[str, Any], duration_ms: float = 0.0):
        event = TelemetryEvent(
            timestamp=datetime.utcnow().isoformat(),
            phase=phase,
            event_type=event_type,
            details=details,
            duration_ms=duration_ms
        )
        self.events.append(event)
        
        if "confidence" in details:
            self.confidence_trajectory.append(details["confidence"])
        
        if "tokens" in details:
            self.total_tokens += details["tokens"]
            # Simple cost estimation (e.g., $0.01 per 1k tokens)
            self.estimated_cost += (details["tokens"] / 1000) * 0.01

        if event_type == "tool_complete":
            tool_name = details.get("tool_name", "unknown")
            if tool_name not in self.tool_stats:
                self.tool_stats[tool_name] = {"calls": 0, "total_ms": 0, "failures": 0}
            self.tool_stats[tool_name]["calls"] += 1
            self.tool_stats[tool_name]["total_ms"] += duration_ms
            if details.get("status") == "failure":
                self.tool_stats[tool_name]["failures"] += 1

    def record_llm_usage(self, input_tokens: int, output_tokens: int, model: str = "unknown"):
        total = input_tokens + output_tokens
        self.record("llm", "usage", {
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "tokens": total
        })

    def record_retrieval_quality(self, semantic_score: float, lexical_score: float, hybrid_score: float):
        self.retrieval_metrics.append({
            "semantic": semantic_score,
            "lexical": lexical_score,
            "hybrid": hybrid_score
        })

    def generate_diagnostics_report(self) -> Dict[str, Any]:
        total_duration = time.time() - self.start_time
        return {
            "execution_summary": {
                "total_duration_s": round(total_duration, 2),
                "total_events": len(self.events),
                "total_tokens": self.total_tokens,
                "estimated_cost_usd": round(self.estimated_cost, 4),
                "final_confidence": self.confidence_trajectory[-1] if self.confidence_trajectory else 0.0
            },
            "tool_performance": self.tool_stats,
            "confidence_trajectory": self.confidence_trajectory,
            "retrieval_quality_avg": {
                "semantic": sum(m["semantic"] for m in self.retrieval_metrics) / max(1, len(self.retrieval_metrics)),
                "hybrid": sum(m["hybrid"] for m in self.retrieval_metrics) / max(1, len(self.retrieval_metrics))
            } if self.retrieval_metrics else {}
        }

    def reset(self):
        self.events.clear()
        self.start_time = time.time()
        self.total_tokens = 0
        self.estimated_cost = 0.0
        self.confidence_trajectory.clear()
        self.tool_stats.clear()
        self.retrieval_metrics.clear()

telemetry = TelemetryTracker()