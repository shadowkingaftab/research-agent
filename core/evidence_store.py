from collections import defaultdict

from models.evidence import Evidence


class EvidenceStore:

    def __init__(self):
        self.clear()

    def clear(self):

        self._facts: list[Evidence] = []
        self._by_category = defaultdict(list)

    def add(self, evidence: Evidence):

        self._facts.append(evidence)

        category = evidence.category or "unknown"

        self._by_category[category].append(evidence)

    def extend(self, evidence_list):

        for evidence in evidence_list:
            self.add(evidence)

    def all(self):

        return list(self._facts)

    def by_category(self, category):

        return list(
            self._by_category.get(category, [])
        )

    def count(self):

        return len(self._facts)

    def summary(self):

        return {

            "total": len(self._facts),

            "categories": {

                category: len(items)

                for category, items

                in self._by_category.items()

            },

        }

    def clear_category(self, category):

        self._facts = [

            evidence

            for evidence in self._facts

            if evidence.category != category

        ]

        self._by_category.pop(category, None)