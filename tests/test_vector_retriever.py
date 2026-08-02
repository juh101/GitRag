from pathlib import Path

import pytest

from retrieval.vector_retriever import VectorRetriever


REPO_PATH = Path("repo_storage") / "pallets" / "markupsafe"


def test_empty_query_raises_error():
    retriever = VectorRetriever(REPO_PATH)

    with pytest.raises(ValueError):
        retriever.retrieve("")


def test_invalid_top_k_raises_error():
    retriever = VectorRetriever(REPO_PATH)

    with pytest.raises(ValueError):
        retriever.retrieve(
            "authentication",
            top_k=0,
        )


def test_retrieve_returns_list():
    retriever = VectorRetriever(REPO_PATH)

    results = retriever.retrieve(
        "escape html",
        top_k=3,
    )

    assert isinstance(results, list)


def test_retrieve_contains_expected_keys():
    retriever = VectorRetriever(REPO_PATH)

    results = retriever.retrieve(
        "escape html",
        top_k=1,
    )

    assert len(results) > 0

    chunk = results[0]

    assert "content" in chunk
    assert "file_path" in chunk
    assert "language" in chunk
    assert "start_line" in chunk
    assert "end_line" in chunk
    assert "chunk_index" in chunk
    assert "score" in chunk


def test_similarity_scores_are_floats():
    retriever = VectorRetriever(REPO_PATH)

    results = retriever.retrieve(
        "escape html",
        top_k=5,
    )

    for chunk in results:
        assert isinstance(chunk["score"], float)