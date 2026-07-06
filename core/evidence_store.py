from collections import defaultdict


class EvidenceStore:

    def __init__(self):
        self.clear()

    def clear(self):

        self._facts = []
        self._by_type = defaultdict(list)

    def add(self, evidence: dict):

        self._facts.append(evidence)

        evidence_type = evidence.get("type", "unknown")

        self._by_type[evidence_type].append(evidence)

    def extend(self, evidence_list):

        for evidence in evidence_list:
            self.add(evidence)

    def all(self):

        return list(self._facts)

    def by_type(self, evidence_type):

        return list(self._by_type.get(evidence_type, []))

    def count(self):

        return len(self._facts)

    def summary(self):

        return {
            "total": len(self._facts),
            "types": {
                key: len(value)
                for key, value in self._by_type.items()
            },
        }

    def clear_type(self, evidence_type):

        self._facts = [
            e
            for e in self._facts
            if e.get("type") != evidence_type
        ]

        self._by_type.pop(evidence_type, None)