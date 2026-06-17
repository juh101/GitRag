from chunking.models import CodeChunk
from ingest.models import CodeDocument


DEFAULT_CHUNK_SIZE = 40
DEFAULT_CHUNK_OVERLAP = 10


def chunk_document(
    document: CodeDocument,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[CodeChunk]:
    """
    Split one CodeDocument into overlapping line-based CodeChunk objects.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative.")

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size."
        )

    lines = document.content.splitlines()

    if not lines:
        return []

    chunks: list[CodeChunk] = []
    step_size = chunk_size - chunk_overlap
    chunk_index = 0

    for start_index in range(0, len(lines), step_size):
        end_index = min(start_index + chunk_size, len(lines))

        chunk_lines = lines[start_index:end_index]
        chunk_content = "\n".join(chunk_lines)

        if not chunk_content.strip():
            continue

        chunk = CodeChunk(
            content=chunk_content,
            file_path=document.file_path,
            file_name=document.file_name,
            language=document.language,
            start_line=start_index + 1,
            end_line=end_index,
            chunk_index=chunk_index,
        )

        chunks.append(chunk)
        chunk_index += 1

        if end_index == len(lines):
            break

    return chunks


def chunk_documents(
    documents: list[CodeDocument],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[CodeChunk]:
    """
    Chunk multiple CodeDocument objects into one flat list of CodeChunk objects.
    """

    all_chunks: list[CodeChunk] = []

    for document in documents:
        document_chunks = chunk_document(
            document=document,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        all_chunks.extend(document_chunks)

    return all_chunks