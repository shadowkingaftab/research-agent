from dataclasses import dataclass
from datetime import datetime


@dataclass
class Source:

    url: str

    title: str = ""

    domain: str = ""

    author: str = ""

    published: str = ""

    accessed: str = datetime.utcnow().isoformat()

    score: float = 0.0

    trusted: bool = False