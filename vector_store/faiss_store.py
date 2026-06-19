from pathlib import Path

import faiss
import numpy as np


class FaissVectorStore:
    """
    Stores embedding vectors in a FAISS index and searches nearest vectors.
    """

    def __init__(self, dimension: int) -> None:
        if dimension <= 0:
            raise ValueError("Vector dimension must be greater than zero.")

        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)

    def add_embeddings(self, embeddings: np.ndarray) -> None:
        """
        Add embedding vectors to the FAISS index.
        """
        if embeddings.ndim != 2:
            raise ValueError("Embeddings must be a 2D array.")

        if embeddings.shape[1] != self.dimension:
            raise ValueError(
                f"Expected embedding dimension {self.dimension}, "
                f"got {embeddings.shape[1]}."
            )

        if embeddings.dtype != np.float32:
            embeddings = embeddings.astype(np.float32)

        self.index.add(embeddings)

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Search for the top_k most similar vectors.

        Returns:
        scores, indices
        """
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        if query_embedding.ndim != 2:
            raise ValueError("Query embedding must be a 1D or 2D array.")

        if query_embedding.shape[1] != self.dimension:
            raise ValueError(
                f"Expected query dimension {self.dimension}, "
                f"got {query_embedding.shape[1]}."
            )

        if query_embedding.dtype != np.float32:
            query_embedding = query_embedding.astype(np.float32)

        scores, indices = self.index.search(query_embedding, top_k)

        return scores, indices

    def save(self, path: str | Path) -> None:
        """
        Save FAISS index to disk.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(path))

    @classmethod
    def load(cls, path: str | Path) -> "FaissVectorStore":
        """
        Load FAISS index from disk.
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"FAISS index not found: {path}")

        index = faiss.read_index(str(path))
        store = cls(index.d)
        store.index = index

        return store

    def count(self) -> int:
        """
        Return number of vectors stored in the index.
        """
        return self.index.ntotal