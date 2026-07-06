from dataclasses import dataclass, field


@dataclass
class Report:

    title: str

    markdown: str

    summary: str = ""

    citations: list[str] = field(default_factory=list)