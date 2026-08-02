import argparse
from pathlib import Path

from chunking.code_chunker import chunk_documents
from embeddings.embed_chunks import embed_chunks
from embeddings.embedding_model import EmbeddingModel
from ingest.clone_repo import clone_repository
from ingest.parse_repo import parse_repository
from vector_store.faiss_store import FaissVectorStore
from vector_store.metadata_store import save_metadata


def ingest_repository(repo_url: str):
    """
    Clone a Git repository, parse supported files,
    chunk them, generate embeddings,
    and build a FAISS index.
    """

    print("Cloning or locating repository...")

    repository_path = clone_repository(repo_url)

    print(f"Repository available at: {repository_path}")
    print("Parsing repository files...")

    documents = parse_repository(repository_path)

    print(f"Total useful files found: {len(documents)}")

    if not documents:
        return [], []

    print("Chunking repository files...")

    chunks = chunk_documents(documents)

    print(f"Total chunks created: {len(chunks)}")

    print("Loading embedding model...")

    embedding_model = EmbeddingModel()

    print("Generating embeddings...")

    embeddings, metadata = embed_chunks(
        chunks,
        embedding_model,
    )

    print(f"Generated {len(embeddings)} embeddings.")
    
    print("Building FAISS index...")

    vector_store = FaissVectorStore(embeddings.shape[1])
    vector_store.add_embeddings(embeddings)

    owner = repository_path.parent.name
    repository = repository_path.name

    save_directory = (
        Path("vector_store")
        / owner
        / repository
    )

    save_directory.mkdir(parents=True, exist_ok=True)

    index_path = save_directory / "index.faiss"
    metadata_path = save_directory / "metadata.json"

    vector_store.save(index_path)
    save_metadata(metadata, metadata_path)

    print(f"FAISS index saved to: {index_path}")
    print(f"Metadata saved to: {metadata_path}")

    return documents, chunks


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clone, parse, chunk and index a GitHub repository."
    )

    parser.add_argument(
        "repo_url",
        help="GitHub repository URL to ingest.",
    )

    args = parser.parse_args()

    documents, chunks = ingest_repository(args.repo_url)

    if not documents:
        print("No supported files found.")
        return

    print("\nSample parsed files:")

    for document in documents[:5]:
        print(
            f"- {document.file_path} "
            f"[{document.language}, {document.size_bytes} bytes]"
        )

    print("\nSample chunks:")

    for chunk in chunks[:5]:
        print(
            f"- {chunk.file_path} "
            f"[lines {chunk.start_line}-{chunk.end_line}, "
            f"chunk {chunk.chunk_index}]"
        )


if __name__ == "__main__":
    main()