from pathlib import Path

import git
from git.exc import InvalidGitRepositoryError, NoSuchPathError


def get_reuse_command(use_uv: bool) -> list[str]:
    """Get the command-line to use when invoking REUSE.

    Args:
        use_uv (bool): If True, REUSE will be run under `uv`. Otherwise, REUSE will be run standalone.

    Returns:
        The command-line to use when invoking REUSE.
    """
    # Return the way in which REUSE should be invoked depending on the value of `use_uv`."""
    return ["uv", "run", "reuse"] if use_uv else ["reuse"]


def find_repo_root(start_hint: Path | None = None) -> Path:
    """Find the root directory of the current git repository.

    Args:
        start_hint (Path | None, optional): If not None, this argument is used as a hint for where to start the search for the root directory. Defaults to None.

    Raises:
        FileNotFoundError: When the search for the root directory fails.

    Returns:
        The root directory of the current git repository.
    """  # noqa: E501
    cwd = (start_hint or Path.cwd()).resolve()
    try:
        git_repo = git.Repo(cwd, search_parent_directories=True)
        return Path(git_repo.working_tree_dir).resolve()
    except (InvalidGitRepositoryError, NoSuchPathError) as e:
        raise FileNotFoundError(f"{cwd} does not seem to be inside a git repository") from e


def find_pyproject_toml(repo_root: Path) -> Path | None:
    """Find the `pyproject.toml` for the current git repository.

    Args:
        repo_root (Path): The root directory of the repository.

    Returns:
        Path | None: The path to `pyproject.toml`, if it exists. None otherwise.
    """
    candidate = repo_root / "pyproject.toml"
    return candidate if candidate.exists() and candidate.is_file() else None
