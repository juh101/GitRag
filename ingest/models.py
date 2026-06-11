from dataclasses import dataclass


@dataclass
class CodeDocument:
    """
    Represents one source-code or documentation file
    extracted from a repository.
    """

    content: str
    file_path: str
    file_name: str
    extension: str
    language: str
    size_bytes: int