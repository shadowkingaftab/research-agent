from difflib import SequenceMatcher

from models.evidence import Evidence


class Retriever:

    def retrieve(
        self,
        query: str,
        evidence,
        limit: int = 50,
    ):

        scored = []

        query = query.lower()

        for item in evidence:

            text = (
                item.fact +
                " " +
                item.summary
            ).lower()

            score = SequenceMatcher(
                None,
                query,
                text,
            ).ratio()

            score *= item.confidence

            scored.append(
                (
                    score,
                    item,
                )
            )

        scored.sort(
            reverse=True,
            key=lambda x: x[0],
        )

        return [

            item

            for _, item

            in scored[:limit]

        ]


retriever = Retriever()