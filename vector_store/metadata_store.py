import json
from pathlib import Path
from typing import Any


def save_metadata(
    metadata: list[dict[str, Any]],
    path: str | Path,
) -> None:
    """
    Save chunk metadata to a JSON file.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2, ensure_ascii=False)


def load_metadata(path: str | Path) -> list[dict[str, Any]]:
    """
    Load chunk metadata from a JSON file.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Metadata file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    if not isinstance(metadata, list):
        raise ValueError("Metadata file must contain a list.")

    return metadata