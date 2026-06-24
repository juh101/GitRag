import numpy as np
import pytest

from vector_store.faiss_store import FaissVectorStore


def test_create_faiss_store():
    store = FaissVectorStore(dimension=3)

    assert store.dimension == 3
    assert store.count() == 0


def test_invalid_dimension_raises_error():
    with pytest.raises(ValueError):
        FaissVectorStore(dimension=0)


def test_add_embeddings_increases_count():
    store = FaissVectorStore(dimension=3)

    embeddings = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype=np.float32,
    )

    store.add_embeddings(embeddings)

    assert store.count() == 2


def test_search_returns_nearest_vector():
    store = FaissVectorStore(dimension=3)

    embeddings = np.array(
        [
            [1.0, 0.0, 0.0],  # vector 0
            [0.0, 1.0, 0.0],  # vector 1
            [0.0, 0.0, 1.0],  # vector 2
        ],
        dtype=np.float32,
    )

    store.add_embeddings(embeddings)

    query = np.array([1.0, 0.0, 0.0], dtype=np.float32)

    scores, indices = store.search(query, top_k=2)

    assert indices.shape == (1, 2)
    assert scores.shape == (1, 2)

    assert indices[0][0] == 0


def test_add_embeddings_wrong_dimension_raises_error():
    store = FaissVectorStore(dimension=3)

    wrong_embeddings = np.array(
        [
            [1.0, 0.0],
        ],
        dtype=np.float32,
    )

    with pytest.raises(ValueError):
        store.add_embeddings(wrong_embeddings)


def test_add_embeddings_must_be_2d():
    store = FaissVectorStore(dimension=3)

    one_dimensional_embedding = np.array(
        [1.0, 0.0, 0.0],
        dtype=np.float32,
    )

    with pytest.raises(ValueError):
        store.add_embeddings(one_dimensional_embedding)


def test_search_wrong_dimension_raises_error():
    store = FaissVectorStore(dimension=3)

    query = np.array([1.0, 0.0], dtype=np.float32)

    with pytest.raises(ValueError):
        store.search(query)


def test_search_invalid_top_k_raises_error():
    store = FaissVectorStore(dimension=3)

    query = np.array([1.0, 0.0, 0.0], dtype=np.float32)

    with pytest.raises(ValueError):
        store.search(query, top_k=0)


def test_save_and_load_faiss_index(tmp_path):
    store = FaissVectorStore(dimension=3)

    embeddings = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        dtype=np.float32,
    )

    store.add_embeddings(embeddings)

    index_path = tmp_path / "index.faiss"

    store.save(index_path)

    loaded_store = FaissVectorStore.load(index_path)

    assert loaded_store.dimension == 3
    assert loaded_store.count() == 2


def test_loaded_index_can_search_correctly(tmp_path):
    store = FaissVectorStore(dimension=3)

    embeddings = np.array(
        [
            [1.0, 0.0, 0.0],  # auth-like vector
            [0.0, 1.0, 0.0],  # payment-like vector
            [0.0, 0.0, 1.0],  # database-like vector
        ],
        dtype=np.float32,
    )

    store.add_embeddings(embeddings)

    index_path = tmp_path / "index.faiss"

    store.save(index_path)

    loaded_store = FaissVectorStore.load(index_path)

    query = np.array([1.0, 0.0, 0.0], dtype=np.float32)

    scores, indices = loaded_store.search(query, top_k=1)

    assert indices.shape == (1, 1)
    assert scores.shape == (1, 1)
    assert indices[0][0] == 0


def test_load_missing_index_raises_error(tmp_path):
    missing_index_path = tmp_path / "missing.index"

    with pytest.raises(FileNotFoundError):
        FaissVectorStore.load(missing_index_path)


def test_save_creates_parent_directory(tmp_path):
    store = FaissVectorStore(dimension=3)

    embeddings = np.array(
        [
            [1.0, 0.0, 0.0],
        ],
        dtype=np.float32,
    )

    store.add_embeddings(embeddings)

    nested_index_path = tmp_path / "owner" / "repo" / "index.faiss"

    store.save(nested_index_path)

    assert nested_index_path.exists()