from __future__ import annotations

from pathlib import Path
from typing import List

from agent.planner import ResearchPlan


def write_report(output_path: str, query: str, plan: ResearchPlan, findings: List[str], verdict: dict) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    report = [
        "# Research Report",
        "",
        f"Query: {query}",
        "",
        "## Plan",
        *[f"- {topic}" for topic in plan.subtopics],
        "",
        "## Findings",
        *[f"- {finding}" for finding in findings],
        "",
        "## Validation",
        f"- Valid: {verdict['is_valid']}",
        f"- Word count: {verdict['word_count']}",
        f"- Preview: {verdict['preview']}",
    ]

    path.write_text("\n".join(report), encoding="utf-8")
    return str(path)
