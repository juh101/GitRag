from pathlib import Path
from urllib.parse import urlparse

from git import GitCommandError, Repo


DEFAULT_REPO_STORAGE = Path("repo_storage")


def extract_repository_identity(repo_url: str) -> tuple[str, str]:
    """
    Extract repository owner and repository name from a GitHub URL.

    Example:
    https://github.com/octocat/Hello-World.git
    returns:
    ("octocat", "Hello-World")
    """
    parsed_url = urlparse(repo_url)

    path_parts = [
        part
        for part in parsed_url.path.strip("/").split("/")
        if part
    ]

    if len(path_parts) < 2:
        raise ValueError(
            "Repository URL must contain both owner and repository name."
        )

    owner_name = path_parts[-2]
    repository_name = path_parts[-1]

    if repository_name.endswith(".git"):
        repository_name = repository_name[:-4]

    if not owner_name or not repository_name:
        raise ValueError(
            "Could not determine repository owner and name from URL."
        )

    return owner_name, repository_name


def clone_repository(
    repo_url: str,
    storage_directory: str | Path = DEFAULT_REPO_STORAGE,
) -> Path:
    """
    Clone a Git repository under:

    repo_storage/<owner>/<repository>
    """
    storage_path = Path(storage_directory)
    storage_path.mkdir(parents=True, exist_ok=True)

    owner_name, repository_name = extract_repository_identity(repo_url)

    owner_directory = storage_path / owner_name
    destination_path = owner_directory / repository_name

    owner_directory.mkdir(parents=True, exist_ok=True)

    if destination_path.exists():
        if (destination_path / ".git").exists():
            return destination_path.resolve()

        raise FileExistsError(
            "Destination exists but is not a Git repository: "
            f"{destination_path}"
        )

    try:
        Repo.clone_from(repo_url, destination_path)
    except GitCommandError as error:
        raise RuntimeError(
            f"Failed to clone repository: {repo_url}"
        ) from error

    return destination_path.resolve()