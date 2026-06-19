from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from embeddings.embedding_model import EmbeddingModel


@patch("embeddings.embedding_model.SentenceTransformer")
def test_embed_texts_returns_float32_array(mock_transformer_class):
    mock_model = MagicMock()

    mock_model.encode.return_value = np.array(
        [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
        ],
        dtype=np.float64,
    )

    mock_transformer_class.return_value = mock_model

    embedding_model = EmbeddingModel("fake-model")

    result = embedding_model.embed_texts(
        ["first chunk", "second chunk"]
    )

    assert result.shape == (2, 3)
    assert result.dtype == np.float32

    mock_model.encode.assert_called_once_with(
        ["first chunk", "second chunk"],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )


@patch("embeddings.embedding_model.SentenceTransformer")
def test_embed_query_returns_single_vector(mock_transformer_class):
    mock_model = MagicMock()

    mock_model.encode.return_value = np.array(
        [[0.1, 0.2, 0.3]],
        dtype=np.float32,
    )

    mock_transformer_class.return_value = mock_model

    embedding_model = EmbeddingModel("fake-model")

    result = embedding_model.embed_query(
        "Where is authentication implemented?"
    )

    assert result.shape == (3,)


@patch("embeddings.embedding_model.SentenceTransformer")
def test_empty_text_list_returns_empty_array(mock_transformer_class):
    mock_transformer_class.return_value = MagicMock()

    embedding_model = EmbeddingModel("fake-model")

    result = embedding_model.embed_texts([])

    assert result.shape == (0, 0)
    assert result.dtype == np.float32


@patch("embeddings.embedding_model.SentenceTransformer")
def test_empty_query_raises_error(mock_transformer_class):
    mock_transformer_class.return_value = MagicMock()

    embedding_model = EmbeddingModel("fake-model")

    with pytest.raises(ValueError):
        embedding_model.embed_query("   ")