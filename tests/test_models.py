from ingest.models import CodeDocument


def test_code_document_creation():
    document = CodeDocument(
        content="print('Hello from GitHub RAG')",
        file_path="src/main.py",
        file_name="main.py",
        extension=".py",
        language="python",
        size_bytes=30,
    )

    assert document.content == "print('Hello from GitHub RAG')"
    assert document.file_path == "src/main.py"
    assert document.file_name == "main.py"
    assert document.extension == ".py"
    assert document.language == "python"
    assert document.size_bytes == 30