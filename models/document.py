from dataclasses import dataclass, field

from models.source import Source


@dataclass
class Document:

    source: Source

    content: str

    summary: str = ""

    language: str = "en"

    tokens: int = 0

    embedding: list[float] = field(default_factory=list)