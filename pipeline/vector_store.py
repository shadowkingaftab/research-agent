import numpy as np

from models.evidence import Evidence


class VectorStore:
    """
    Stores evidence together with its embedding and
    performs cosine similarity search.
    """

    def __init__(self):

        self.clear()

    def clear(self):

        self._items: list[Evidence] = []
        self._matrix = None

    def add(self, evidence: Evidence):

        if not evidence.embedding:
            return

        self._items.append(evidence)

        vector = np.asarray(
            evidence.embedding,
            dtype=np.float32,
        )

        if self._matrix is None:

            self._matrix = vector.reshape(1, -1)

        else:

            self._matrix = np.vstack(
                (
                    self._matrix,
                    vector,
                )
            )

    def count(self):

        return len(self._items)

    def all(self):

        return list(self._items)

    def search(
        self,
        query_embedding,
        limit=20,
        min_score=0.35,
    ):

        if self._matrix is None:

            return []

        query = np.asarray(
            query_embedding,
            dtype=np.float32,
        )

        scores = self._matrix @ query

        ranked = sorted(

            zip(
                scores,
                self._items,
            ),

            key=lambda x: x[0],

            reverse=True,

        )

        results = []

        for score, evidence in ranked:

            if score < min_score:
                continue

            results.append(

                {

                    "score": float(score),

                    "evidence": evidence,

                }

            )

            if len(results) >= limit:
                break

        return results


vector_store = VectorStore()