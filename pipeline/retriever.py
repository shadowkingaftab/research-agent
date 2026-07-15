from difflib import SequenceMatcher

import numpy as np

from pipeline.embedder import embedder


class Retriever:

    SEMANTIC_WEIGHT = 0.7
    LEXICAL_WEIGHT = 0.3

    MEMORY_BOOST = 1.05

    def _lexical_score(self, query: str, item) -> float:

        text = (item.fact + " " + item.summary).lower()

        return SequenceMatcher(None, query, text).ratio()

    def _semantic_score(self, query_embedding, item) -> float:

        if not item.embedding or not query_embedding:
            return 0.0

        query_vec = np.asarray(query_embedding, dtype=np.float32)
        item_vec = np.asarray(item.embedding, dtype=np.float32)

        if query_vec.shape != item_vec.shape:
            return 0.0

        # Embeddings are already normalized by Embedder, so the
        # dot product is equivalent to cosine similarity.
        score = float(query_vec @ item_vec)

        return max(0.0, score)

    def retrieve(
        self,
        query: str,
        evidence,
        limit: int = 50,
    ):

        if not evidence:
            return []

        query_lower = query.lower()
        query_embedding = embedder.encode(query)

        scored = []

        for item in evidence:

            lexical = self._lexical_score(query_lower, item)
            semantic = self._semantic_score(query_embedding, item)

            # If there's no embedding yet, fall back to pure lexical
            # instead of letting a zero semantic score drag it down.
            if semantic == 0.0 and not item.embedding:
                combined = lexical
            else:
                combined = (
                    self.SEMANTIC_WEIGHT * semantic
                    + self.LEXICAL_WEIGHT * lexical
                )

            score = combined * item.confidence

            if item.metadata.get("from_memory"):
                score *= self.MEMORY_BOOST

            item.retrieval_score = round(score, 4)

            scored.append((score, item))

        scored.sort(reverse=True, key=lambda x: x[0])

        return [item for _, item in scored[:limit]]


retriever = Retriever()