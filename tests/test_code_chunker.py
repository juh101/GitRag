import pytest

from chunking.code_chunker import (
    chunk_document,
    chunk_documents,
)
from ingest.models import CodeDocument


def make_document(content: str) -> CodeDocument:
    return CodeDocument(
        content=content,
        file_path="src/main.py",
        file_name="main.py",
        extension=".py",
        language="python",
        size_bytes=len(content.encode("utf-8")),
    )


def test_small_document_creates_one_chunk():
    document = make_document(
        "line 1\nline 2\nline 3"
    )

    chunks = chunk_document(
        document,
        chunk_size=10,
        chunk_overlap=2,
    )

    assert len(chunks) == 1
    assert chunks[0].content == "line 1\nline 2\nline 3"
    assert chunks[0].start_line == 1
    assert chunks[0].end_line == 3
    assert chunks[0].chunk_index == 0


def test_document_is_split_with_overlap():
    content = "\n".join(
        f"line {number}"
        for number in range(1, 11)
    )

    document = make_document(content)

    chunks = chunk_document(
        document,
        chunk_size=4,
        chunk_overlap=1,
    )

    assert len(chunks) == 3

    assert chunks[0].start_line == 1
    assert chunks[0].end_line == 4

    assert chunks[1].start_line == 4
    assert chunks[1].end_line == 7

    assert chunks[2].start_line == 7
    assert chunks[2].end_line == 10


def test_chunk_metadata_is_preserved():
    document = make_document("print('hello')")

    chunks = chunk_document(document)

    assert chunks[0].file_path == document.file_path
    assert chunks[0].file_name == document.file_name
    assert chunks[0].language == document.language


def test_empty_document_returns_empty_list():
    document = make_document("")

    assert chunk_document(document) == []


def test_invalid_chunk_size_raises_error():
    document = make_document("line 1")

    with pytest.raises(ValueError):
        chunk_document(
            document,
            chunk_size=0,
            chunk_overlap=0,
        )


def test_overlap_equal_to_chunk_size_raises_error():
    document = make_document("line 1")

    with pytest.raises(ValueError):
        chunk_document(
            document,
            chunk_size=10,
            chunk_overlap=10,
        )


def test_chunk_multiple_documents():
    documents = [
        make_document("file one"),
        make_document("file two"),
    ]

    chunks = chunk_documents(documents)

    assert len(chunks) == 2