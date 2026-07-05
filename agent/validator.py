from __future__ import annotations

from typing import List


def validate_content(content: List[str], min_words: int = 40) -> dict:
    combined = " ".join(content)
    word_count = len(combined.split())
    return {
        "is_valid": word_count >= min_words,
        "word_count": word_count,
        "preview": combined[:240],
    }
