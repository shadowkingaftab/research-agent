from dataclasses import dataclass, field

from models.document import Document
from models.evidence import Evidence
from models.report import Report


@dataclass
class Project:

    goal: str

    documents: list[Document] = field(default_factory=list)

    evidence: list[Evidence] = field(default_factory=list)

    report: Report | None = None