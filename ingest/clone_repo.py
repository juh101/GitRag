from pathlib import Path
from urllib.parse import urlparse

from git import GitCommandError, Repo

DEFAULT_REPO_STORAGE = Path("repo_storage")


def extract_repository_name(repo_url: str) -> str:
    """
    Extract the repository name from a GitHub repository URL.

    Example:
    https://github.com/psf/requests.git -> requests
    """
    parsed_url = urlparse(repo_url)

    repository_name = Path(parsed_url.path).name

    if repository_name.endswith(".git"):
        repository_name = repository_name[:-4]

    if not repository_name:
        raise ValueError("Could not determine repository name from URL.")

    return repository_name


def clone_repository(
    repo_url: str,
    storage_directory: str | Path = DEFAULT_REPO_STORAGE,
) -> Path:
    """
    Clone a Git repository into local storage.

    If the repository already exists locally, return its existing path.
    """
    storage_path = Path(storage_directory)
    storage_path.mkdir(parents=True, exist_ok=True)

    repository_name = extract_repository_name(repo_url)
    destination_path = storage_path / repository_name

    if destination_path.exists():
        if (destination_path / ".git").exists():
            return destination_path.resolve()

        raise FileExistsError(
            f"Destination already exists but is not a Git repository: "
            f"{destination_path}"
        )

    try:
        Repo.clone_from(repo_url, destination_path)
    except GitCommandError as error:
        raise RuntimeError(
            f"Failed to clone repository: {repo_url}"
        ) from error

    return destination_path.resolve()