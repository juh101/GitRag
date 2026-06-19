from typing import Any

import numpy as np

from chunking.models import CodeChunk
from embeddings.embedding_model import EmbeddingModel


def create_chunk_metadata(chunk: CodeChunk) -> dict[str, Any]:
    """
    Create metadata for one code chunk.

    This metadata will later help map a vector back to its original source.
    """
    return {
        "content": chunk.content,
        "file_path": chunk.file_path,
        "file_name": chunk.file_name,
        "language": chunk.language,
        "start_line": chunk.start_line,
        "end_line": chunk.end_line,
        "chunk_index": chunk.chunk_index,
    }


def embed_chunks(
    chunks: list[CodeChunk],
    embedding_model: EmbeddingModel,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    """
    Convert CodeChunk objects into an embedding matrix and metadata list.
    """
    if not chunks:
        return np.empty((0, 0), dtype=np.float32), []

    texts = [chunk.content for chunk in chunks]

    embeddings = embedding_model.embed_texts(texts)

    metadata = [
        create_chunk_metadata(chunk)
        for chunk in chunks
    ]

    return embeddings, metadata