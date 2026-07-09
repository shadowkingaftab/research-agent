from functools import lru_cache

from sentence_transformers import SentenceTransformer


class Embedder:
    """
    Central embedding service.

    Loads the embedding model only once and provides a simple
    interface for converting text into vectors.
    """

    def __init__(self):

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    @lru_cache(maxsize=5000)
    def encode(self, text: str):

        if not text:
            return []

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        return embedding.tolist()

    def encode_many(self, texts):

        if not texts:
            return []

        vectors = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        return [
            vector.tolist()
            for vector in vectors
        ]


embedder = Embedder()