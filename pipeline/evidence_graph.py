import re
from difflib import SequenceMatcher
from itertools import combinations


class ContradictionDetector:
    """
    Flags pairs of evidence that appear to be about the same subject
    (high entity/keyword overlap) but disagree on the substance
    (low text similarity, or explicit conflicting numbers).

    This is a heuristic pre-filter, not a semantic judgement. It is
    meant to surface candidate conflicts for the Writer/human to
    resolve, not to silently decide which fact is correct.
    """

    ENTITY_OVERLAP_THRESHOLD = 0.4
    TEXT_SIMILARITY_THRESHOLD = 0.5

    NUMBER_PATTERN = re.compile(r"\d+(?:\.\d+)?")

    def _tag_set(self, item):
        return set(e.lower() for e in item.entities) | set(
            k.lower() for k in item.keywords
        )

    def _jaccard(self, a: set, b: set) -> float:
        if not a or not b:
            return 0.0
        return len(a & b) / len(a | b)

    def _text_similarity(self, a, b) -> float:
        return SequenceMatcher(None, a.fact.lower(), b.fact.lower()).ratio()

    def _conflicting_numbers(self, a, b):
        nums_a = set(self.NUMBER_PATTERN.findall(a.fact))
        nums_b = set(self.NUMBER_PATTERN.findall(b.fact))

        if not nums_a or not nums_b:
            return False

        return nums_a != nums_b and not nums_a.issubset(nums_b) and not nums_b.issubset(nums_a)

    def find(self, evidence_list):

        contradictions = []

        # Only compare within the same category: a "company" fact
        # and a "person" fact sharing a keyword isn't a contradiction.
        by_category = {}

        for item in evidence_list:
            by_category.setdefault(item.category, []).append(item)

        for category, items in by_category.items():

            for a, b in combinations(items, 2):

                tags_a = self._tag_set(a)
                tags_b = self._tag_set(b)

                overlap = self._jaccard(tags_a, tags_b)

                if overlap < self.ENTITY_OVERLAP_THRESHOLD:
                    continue

                similarity = self._text_similarity(a, b)
                numbers_conflict = self._conflicting_numbers(a, b)

                if similarity >= self.TEXT_SIMILARITY_THRESHOLD and not numbers_conflict:
                    continue

                severity = "high" if numbers_conflict else "medium"

                contradictions.append(
                    {
                        "category": category,
                        "evidence_a": a,
                        "evidence_b": b,
                        "entity_overlap": round(overlap, 3),
                        "text_similarity": round(similarity, 3),
                        "conflicting_numbers": numbers_conflict,
                        "severity": severity,
                    }
                )

        contradictions.sort(
            key=lambda c: (c["severity"] != "high", -c["entity_overlap"])
        )

        return contradictions


contradiction_detector = ContradictionDetector()

class KnowledgeGraph:
    """
    Builds a lightweight entity co-occurrence graph from evidence.

    Nodes are subjects (companies/people/products) and the
    entities/keywords attached to them. Edges connect a subject to
    the entities it was mentioned alongside, weighted by how many
    evidence items support that connection.

    Dependency-free by design (no networkx) so it can run anywhere
    this project runs.
    """

    SUBJECT_CATEGORIES = {"company", "person", "product"}

    def __init__(self):
        self.clear()

    def clear(self):
        self.nodes = {}   # id -> {"label", "type", "mentions"}
        self.edges = {}   # (id_a, id_b) sorted tuple -> {"weight", "sources"}

    def _add_node(self, node_id: str, node_type: str):

        if not node_id:
            return

        node = self.nodes.setdefault(
            node_id,
            {"label": node_id, "type": node_type, "mentions": 0},
        )

        node["mentions"] += 1

    def _add_edge(self, a: str, b: str, source_url: str):

        if not a or not b or a == b:
            return

        key = tuple(sorted((a, b)))

        edge = self.edges.setdefault(
            key, {"weight": 0, "sources": set()}
        )

        edge["weight"] += 1
        edge["sources"].add(source_url)

    def build(self, evidence_list):

        self.clear()

        for item in evidence_list:

            related = list(item.entities) + list(item.keywords)

            is_subject = item.category in self.SUBJECT_CATEGORIES

            subject_id = item.fact if is_subject else None

            if subject_id:
                self._add_node(subject_id, item.category)

            for tag in related:

                self._add_node(tag, "entity")

                if subject_id:
                    self._add_edge(subject_id, tag, item.source_url)

            # Also connect co-mentioned entities/keywords to each
            # other within the same evidence item.
            for a, b in zip(related, related[1:]):
                self._add_edge(a, b, item.source_url)

        return self

    def to_dict(self):

        return {
            "nodes": [
                {"id": node_id, **data}
                for node_id, data in self.nodes.items()
            ],
            "edges": [
                {
                    "source": pair[0],
                    "target": pair[1],
                    "weight": data["weight"],
                }
                for pair, data in self.edges.items()
            ],
        }

    def to_mermaid(self, max_nodes: int = 25) -> str:
        """
        Renders the highest-mention nodes as a Mermaid graph, safe to
        drop directly into a Markdown report.
        """

        if not self.nodes:
            return ""

        top_nodes = sorted(
            self.nodes.items(),
            key=lambda kv: kv[1]["mentions"],
            reverse=True,
        )[:max_nodes]

        top_ids = {node_id for node_id, _ in top_nodes}

        def safe_id(text: str) -> str:
            return "".join(c if c.isalnum() else "_" for c in text)[:40]

        lines = ["```mermaid", "graph TD"]

        for pair, data in self.edges.items():

            a, b = pair

            if a not in top_ids or b not in top_ids:
                continue

            lines.append(
                f'    {safe_id(a)}["{a[:40]}"] '
                f'-- {data["weight"]} --> {safe_id(b)}["{b[:40]}"]'
            )

        lines.append("```")

        return "\n".join(lines) if len(lines) > 2 else ""


knowledge_graph = KnowledgeGraph()