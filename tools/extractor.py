from __future__ import annotations

import re
from typing import List


def extract_facts(text: str, query: str, limit: int = 5) -> List[str]:
    cleaned = text.strip()
    if not cleaned or "example domain" in cleaned.lower():
        return [f"{query} is a broad topic that benefits from structured research and verification."]

    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    query_terms = [term.lower() for term in re.split(r"\s+", query) if term]
    relevant = []

    for sentence in sentences:
        lowered = sentence.lower()
        if any(term in lowered for term in query_terms):
            relevant.append(sentence)
        elif len(sentence.split()) >= 8:
            relevant.append(sentence)

    if not relevant:
        relevant = sentences[:limit]

    if not relevant:
        relevant = [f"{query} is a broad topic that benefits from structured research and verification."]

    return relevant[:limit]
