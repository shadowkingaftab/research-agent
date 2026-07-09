from collections import defaultdict

from models.evidence import Evidence


class EvidenceStore:

    def __init__(self):

        self.clear()

    def clear(self):

        self._evidence = {}
        self._by_category = defaultdict(list)

    def add(self, evidence: Evidence):

        self._evidence[evidence.id] = evidence

        if evidence.category:

            self._by_category[evidence.category].append(
                evidence.id
            )

    def get(self, evidence_id: str):

        return self._evidence.get(evidence_id)

    def exists(self, evidence_id: str):

        return evidence_id in self._evidence

    def remove(self, evidence_id: str):

        evidence = self._evidence.pop(evidence_id, None)

        if evidence is None:
            return

        if evidence.category in self._by_category:

            ids = self._by_category[evidence.category]

            if evidence_id in ids:

                ids.remove(evidence_id)

    def all(self):

        return list(self._evidence.values())

    def count(self):

        return len(self._evidence)

    def by_category(self, category: str):

        ids = self._by_category.get(category, [])

        return [
            self._evidence[i]
            for i in ids
            if i in self._evidence
        ]

    def search(self, text: str):

        text = text.lower()

        results = []

        for evidence in self._evidence.values():

            if (
                text in evidence.fact.lower()
                or text in evidence.summary.lower()
            ):

                results.append(evidence)

        return results


evidence_store = EvidenceStore()