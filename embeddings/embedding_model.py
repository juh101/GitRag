from collections.abc import Sequence

import numpy as np
from sentence_transformers import SentenceTransformer


DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"


class EmbeddingModel:
    """
    Wrapper around SentenceTransformer for generating text embeddings.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
    ) -> None:
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed_texts(
        self,
        texts: Sequence[str],
    ) -> np.ndarray:
        """
        Convert multiple text inputs into normalized embedding vectors.
        """
        if not texts:
            return np.empty((0, 0), dtype=np.float32)

        embeddings = self.model.encode(
            list(texts),
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        return embeddings.astype(np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """
        Convert one user query into a normalized embedding vector.
        """
        if not query.strip():
            raise ValueError("Query cannot be empty.")

        embeddings = self.embed_texts([query])

        return embeddings[0]