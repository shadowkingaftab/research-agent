from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Evidence:

    # -------------------------
    # Core Information
    # -------------------------

    fact: str
    category: str = ""
    summary: str = ""

    # -------------------------
    # Source Information
    # -------------------------

    source_url: str = ""
    source_title: str = ""
    document_id: str = ""
    chunk_id: int = 0

    # -------------------------
    # Quality
    # -------------------------

    confidence: float = 0.0

    # -------------------------
    # NLP Information
    # -------------------------

    entities: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)

    # -------------------------
    # Supporting Evidence
    # -------------------------

    supporting_quotes: list[str] = field(default_factory=list)
    supporting_sources: list[str] = field(default_factory=list)

    # -------------------------
    # Semantic Search
    # -------------------------

    embedding: list[float] = field(default_factory=list)

    retrieval_score: float = 0.0

    # -------------------------
    # Metadata
    # -------------------------

    metadata: dict = field(default_factory=dict)

    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )

    def to_dict(self):

        return {
            "fact": self.fact,
            "category": self.category,
            "summary": self.summary,
            "source_url": self.source_url,
            "source_title": self.source_title,
            "document_id": self.document_id,
            "chunk_id": self.chunk_id,
            "confidence": self.confidence,
            "entities": self.entities,
            "keywords": self.keywords,
            "supporting_quotes": self.supporting_quotes,
            "supporting_sources": self.supporting_sources,
            "embedding": self.embedding,
            "retrieval_score": self.retrieval_score,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }