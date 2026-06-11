import os
from pathlib import Path

from ingest.file_filter import (
    should_ignore_directory,
    should_process_file,
)
from ingest.models import CodeDocument


EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".go": "go",
    ".rs": "rust",
    ".php": "php",
    ".rb": "ruby",
    ".kt": "kotlin",
    ".swift": "swift",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".sql": "sql",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".xml": "xml",
    ".md": "markdown",
    ".txt": "text",
}


def detect_language(file_path: Path) -> str:
    """
    Detect the programming language using the file extension.
    """
    return EXTENSION_TO_LANGUAGE.get(
        file_path.suffix.lower(),
        "unknown",
    )


def read_file_content(file_path: Path) -> str | None:
    """
    Read a text file safely.

    Returns None when the file cannot be decoded or read.
    """
    try:
        return file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def parse_repository(repository_path: str | Path) -> list[CodeDocument]:
    """
    Walk through a repository and return supported files
    as CodeDocument objects.
    """
    repository_path = Path(repository_path).resolve()

    if not repository_path.exists():
        raise FileNotFoundError(
            f"Repository path does not exist: {repository_path}"
        )

    if not repository_path.is_dir():
        raise NotADirectoryError(
            f"Repository path is not a directory: {repository_path}"
        )

    documents: list[CodeDocument] = []

    for root, directories, files in os.walk(repository_path):
        directories[:] = [
            directory
            for directory in directories
            if not should_ignore_directory(directory)
        ]

        root_path = Path(root)

        for file_name in files:
            file_path = root_path / file_name

            if not should_process_file(file_path):
                continue

            content = read_file_content(file_path)

            if content is None:
                continue

            relative_path = file_path.relative_to(repository_path)

            document = CodeDocument(
                content=content,
                file_path=relative_path.as_posix(),
                file_name=file_path.name,
                extension=file_path.suffix.lower(),
                language=detect_language(file_path),
                size_bytes=file_path.stat().st_size,
            )

            documents.append(document)

    return documents