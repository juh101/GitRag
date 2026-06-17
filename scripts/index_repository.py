import argparse

from chunking.code_chunker import chunk_documents
from ingest.clone_repo import clone_repository
from ingest.parse_repo import parse_repository


def ingest_repository(repo_url: str):
    """
    Clone a Git repository, parse supported files,
    and split them into retrievable code chunks.
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

    return documents, chunks


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clone, parse, and chunk a GitHub repository."
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