from dataclasses import dataclass


@dataclass
class CodeChunk:
    """
    Represents a smaller retrievable section of a repository file.
    """

    content: str
    file_path: str
    file_name: str
    language: str
    start_line: int
    end_line: int
    chunk_index: int
    
    
    