from pathlib import Path

import git

from reuse_license_utils.config import REUSE_EXEMPT_DIRS, REUSE_EXEMPT_PREFIXES, LicenseUtilsConfig


def _expand_patterns(repo_root: Path, patterns: list[str]) -> set[Path]:
    """Generate a set of files that match a set of glob patterns applied against the repo root."""
    expanded = set()
    for pattern in patterns:
        for matched_file in repo_root.glob(pattern):
            expanded.add(matched_file.expanduser().resolve())
    return expanded


def collect_header_files(repo_root: Path, config: LicenseUtilsConfig, header_group_id: str) -> list[Path]:
    """
    Collect a sorted list of files to which license headers should be applied.

    Args:
        repo_root: the path to the root of the repo.
        config: the configuration for reuse-license-utils.
        header_group_id: the group ID (i.e., key) under the config's `headers` field.

    Returns:
        A sorted list of the header files for the specified group.
    """
    # Get all files that are excluded from consideration by REUSE or by our tool
    excluded = _expand_patterns(
        repo_root,
        [f"{d}/**" for d in REUSE_EXEMPT_DIRS] + config.header_groups[header_group_id].exclude_patterns,
    )

    # Get all non-excluded files matching the include patterns of the group
    header_files = set()
    for pattern in config.header_groups[header_group_id].include_patterns:
        for matched_file in repo_root.glob(pattern):
            if not matched_file.is_file() or matched_file.resolve() in excluded:
                continue
            header_files.add(matched_file)

    # Sort and return the header files that have been matched
    return sorted(header_files)


def collect_reuse_toml_files(repo_root: Path, config: LicenseUtilsConfig) -> list[Path]:
    """
    Collect the files that need to be specified in REUSE.toml.

    Files that need to be specified in REUSE.toml are essentially all files in the repo
    that do **not** fall in one of the following categories:

    - Files that have license headers
    - Files that are not tracked by version control
    - Files that are exempted by the REUSE spec

    Args:
        repo_root: the path to the root of the repo.
        config: the configuration for reuse-license-utils.

    Returns:
        A sorted list of the files that need to be specified in REUSE.toml.
    """
    # Get all files tracked by git using GitPython
    git_repo = git.Repo(repo_root)
    tracked_files = [Path(entry.path) for entry in git_repo.index.entries.values()]
    # Get all files that should have headers
    files_with_headers = set()
    for group_id in config.header_groups.keys():
        files_with_headers = files_with_headers | set(collect_header_files(repo_root, config, group_id))
    # Filter out files that should be excluded from REUSE.toml and return the rest
    return sorted(f for f in tracked_files if f not in files_with_headers and not is_reuse_exempt(f))


def is_reuse_exempt(path: Path) -> bool:
    """Check if a file is exempted by the REUSE spec (as it is encoded in this tool).

    Args:
        path: the path to the file being checked

    Returns:
        True if the file is REUSE-exempt. False otherwise.
    """
    # The first part of the condition (before the OR) checks if the file is within
    # any of the exempt directories. The second part of the condition (after the OR) checks
    # if the file name starts with any of the exempt prefixes. If either condition is true,
    # the path is REUSE-exempt. Otherwise, the path is not REUSE-exempt.
    return any(path.is_relative_to(exempt_dir) for exempt_dir in REUSE_EXEMPT_DIRS) or any(
        path.name.upper().startswith(prefix) for prefix in REUSE_EXEMPT_PREFIXES
    )
