import numpy as np

from chunking.models import CodeChunk
from embeddings.embed_chunks import (
    create_chunk_metadata,
    embed_chunks,
)


class FakeEmbeddingModel:
    def embed_texts(self, texts):
        return np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ],
            dtype=np.float32,
        )


def make_chunk(content: str, chunk_index: int) -> CodeChunk:
    return CodeChunk(
        content=content,
        file_path="src/main.py",
        file_name="main.py",
        language="python",
        start_line=1 + chunk_index * 10,
        end_line=10 + chunk_index * 10,
        chunk_index=chunk_index,
    )


def test_create_chunk_metadata():
    chunk = make_chunk(
        content="print('hello')",
        chunk_index=0,
    )

    metadata = create_chunk_metadata(chunk)

    assert metadata["content"] == "print('hello')"
    assert metadata["file_path"] == "src/main.py"
    assert metadata["file_name"] == "main.py"
    assert metadata["language"] == "python"
    assert metadata["start_line"] == 1
    assert metadata["end_line"] == 10
    assert metadata["chunk_index"] == 0


def test_embed_chunks_returns_embeddings_and_metadata():
    chunks = [
        make_chunk("first chunk", 0),
        make_chunk("second chunk", 1),
    ]

    embedding_model = FakeEmbeddingModel()

    embeddings, metadata = embed_chunks(
        chunks=chunks,
        embedding_model=embedding_model,
    )

    assert embeddings.shape == (2, 3)
    assert embeddings.dtype == np.float32

    assert len(metadata) == 2
    assert metadata[0]["content"] == "first chunk"
    assert metadata[1]["content"] == "second chunk"


def test_embed_chunks_empty_input():
    embedding_model = FakeEmbeddingModel()

    embeddings, metadata = embed_chunks(
        chunks=[],
        embedding_model=embedding_model,
    )

    assert embeddings.shape == (0, 0)
    assert embeddings.dtype == np.float32
    assert metadata == []