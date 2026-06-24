import json

import pytest

from vector_store.metadata_store import (
    load_metadata,
    save_metadata,
)


def test_save_and_load_metadata(tmp_path):
    metadata = [
        {
            "content": "print('hello')",
            "file_path": "src/main.py",
            "file_name": "main.py",
            "language": "python",
            "start_line": 1,
            "end_line": 1,
            "chunk_index": 0,
        }
    ]

    metadata_path = tmp_path / "metadata.json"

    save_metadata(metadata, metadata_path)

    loaded_metadata = load_metadata(metadata_path)

    assert loaded_metadata == metadata


def test_save_metadata_creates_parent_directory(tmp_path):
    metadata = [
        {
            "content": "print('hello')",
            "file_path": "src/main.py",
            "file_name": "main.py",
            "language": "python",
            "start_line": 1,
            "end_line": 1,
            "chunk_index": 0,
        }
    ]

    metadata_path = tmp_path / "owner" / "repo" / "metadata.json"

    save_metadata(metadata, metadata_path)

    assert metadata_path.exists()


def test_load_missing_metadata_raises_error(tmp_path):
    missing_path = tmp_path / "missing_metadata.json"

    with pytest.raises(FileNotFoundError):
        load_metadata(missing_path)


def test_load_metadata_requires_list(tmp_path):
    metadata_path = tmp_path / "metadata.json"

    with metadata_path.open("w", encoding="utf-8") as file:
        json.dump(
            {"file_path": "src/main.py"},
            file,
        )

    with pytest.raises(ValueError):
        load_metadata(metadata_path)