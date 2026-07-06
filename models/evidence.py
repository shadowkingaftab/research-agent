from dataclasses import dataclass, field


@dataclass
class Evidence:

    fact: str

    source_url: str

    confidence: float = 0.0

    category: str = ""

    entities: list[str] = field(default_factory=list)

    supporting_quotes: list[str] = field(default_factory=list)