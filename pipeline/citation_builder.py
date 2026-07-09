from models.evidence import Evidence


class CitationBuilder:

    def build(self, evidence_list: list[Evidence]):

        citations = {}

        for evidence in evidence_list:

            fact = evidence.fact.strip()

            if not fact:
                continue

            citations.setdefault(fact, set())

            if evidence.source_url:
                citations[fact].add(evidence.source_url)

        return {
            fact: sorted(urls)
            for fact, urls in citations.items()
        }


citation_builder = CitationBuilder()