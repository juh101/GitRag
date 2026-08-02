from pathlib import Path
from typing import Any

from embeddings.embedding_model import EmbeddingModel
from vector_store.faiss_store import FaissVectorStore
from vector_store.metadata_store import load_metadata


class VectorRetriever:
    """
    Performs semantic retrieval over a repository using
    SentenceTransformer embeddings and a FAISS vector index.
    """

    def __init__(self, repository_path: str | Path) -> None:
        self.repository_path = Path(repository_path)

        owner = self.repository_path.parent.name
        repository = self.repository_path.name

        vector_store_directory = (
            Path("vector_store")
            / owner
            / repository
        )

        self.index_path = vector_store_directory / "index.faiss"
        self.metadata_path = vector_store_directory / "metadata.json"

        self.embedding_model = EmbeddingModel()
        self.vector_store = FaissVectorStore.load(self.index_path)
        self.metadata = load_metadata(self.metadata_path)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Retrieve the top-k most relevant code chunks for a query.
        """

        if not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        query_embedding = self.embedding_model.embed_query(query)

        scores, indices = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
        )

        retrieved_chunks: list[dict[str, Any]] = []

        for score, index in zip(scores[0], indices[0]):

            if index == -1:
                continue

            chunk = self.metadata[index].copy()

            chunk["score"] = float(score)

            retrieved_chunks.append(chunk)

        return retrieved_chunks