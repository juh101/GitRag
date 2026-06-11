from pathlib import Path


IGNORED_DIRECTORIES = {
    ".git",
    ".github",
    ".idea",
    ".vscode",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "env",
    "dist",
    "build",
    "coverage",
    ".next",
    ".pytest_cache",
    ".mypy_cache",
}


SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".cs",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".kt",
    ".swift",
    ".html",
    ".css",
    ".scss",
    ".sql",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".xml",
    ".md",
    ".txt",
}


MAX_FILE_SIZE_BYTES = 1_000_000


def should_ignore_directory(directory_name: str) -> bool:
    return directory_name in IGNORED_DIRECTORIES


def is_supported_file(file_path: Path) -> bool:
    return file_path.suffix.lower() in SUPPORTED_EXTENSIONS


def is_file_too_large(file_path: Path) -> bool:
    return file_path.stat().st_size > MAX_FILE_SIZE_BYTES


def should_process_file(file_path: Path) -> bool:
    if not file_path.is_file():
        return False

    if not is_supported_file(file_path):
        return False

    if is_file_too_large(file_path):
        return False

    return True