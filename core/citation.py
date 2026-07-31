# core/citation.py
import uuid
from typing import List, Dict
from models.evidence import Evidence

class CitationEngine:
    def __init__(self):
        self.claim_to_evidence: Dict[str, List[str]] = {} # claim_text -> [evidence_ids]
        self.evidence_registry: Dict[str, Evidence] = {}

    def register_evidence(self, evidence: Evidence) -> str:
        cid = f"CITE-{uuid.uuid4().hex[:8].upper()}"
        evidence.citation_id = cid
        self.evidence_registry[cid] = evidence
        return cid

    def link_claim(self, claim: str, evidence_ids: List[str]):
        self.claim_to_evidence[claim] = evidence_ids

    def render_inline(self, claim: str) -> str:
        cids = self.claim_to_evidence.get(claim, [])
        if not cids:
            return claim
        citations = ", ".join([f"[{cid}]" for cid in cids])
        return f"{claim} {citations}"

    def generate_bibliography(self) -> str:
        bib = []
        for cid, evidence in self.evidence_registry.items():
            source_quality = evidence.metadata.get("source_quality", "Unknown")
            bib.append(f"- **[{cid}]** {evidence.source_url} | Confidence: {evidence.confidence:.2f} | Quality: {source_quality}")
        return "\n".join(bib)

citation_engine = CitationEngine()