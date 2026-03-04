import subprocess
from pathlib import Path

from reuse_license_utils.config import LicenseUtilsConfig
from reuse_license_utils.identify_files import _expand_patterns, collect_reuse_toml_files
from reuse_license_utils.utils import get_reuse_command


def verify_repo(
    repo_root: Path,
    use_uv: bool = False,
    quiet: bool = False,
    check: bool = True,
) -> tuple[bool, subprocess.CompletedProcess]:
    """Run `reuse lint` against the repository to verify REUSE compliance.

    Args:
        repo_root (Path): The path to the repository root.
        use_uv (bool, optional): If True, invoke REUSE as `uv run reuse` instead of `reuse`. Defaults to False.
        quiet (bool, optional): If True, pass `--quiet` to `reuse lint`. Defaults to False.
        check (bool, optional): If True, pass `check=True` to `subprocess.run`. Defaults to True.

    Returns:
        A `CompletedProcess` instance for the run on `reuse lint`.
    """
    reuse_cmd = get_reuse_command(use_uv)
    subprocess_cmd = [*reuse_cmd, "lint"]
    if quiet:
        subprocess_cmd.append("--quiet")
    return subprocess.run(subprocess_cmd, cwd=repo_root, check=check)


def verify_reuse_toml_paths(repo_root: Path, config: LicenseUtilsConfig) -> tuple[bool, set[Path], set[Path]]:
    """Check if the paths in the `reuse_toml_paths` section of the config cover all the files that should be included in REUSE.toml.

    Args:
        repo_root (Path): The path to the repository root.
        config (LicenseUtilsConfig): The reuse-license-utils config.

    Returns:
        A tuple of:
          - A boolean that is True if the paths in the `reuse_toml_paths` section of the config cover all the files that should be included in REUSE.toml. False otherwise.
          - A set of files that should be represented in REUSE.toml, but would not be based on the config.
          - A set of files that would be represented in REUSE.toml based on the config, but should not be.
    """  # noqa: E501
    # Get the files that are expected to be covered by REUSE.toml
    expected_reuse_toml_files = set(collect_reuse_toml_files(repo_root, config))
    # Get the files that will actually be covered by a generated REUSE.toml
    expanded_reuse_toml_paths = _expand_patterns(
        repo_root,
        [path_config.path for path_config in config.reuse_toml_paths],
    )
    # Use set difference to find the expected files that would not be covered by a generated REUSE.toml
    missing_files = expected_reuse_toml_files - expanded_reuse_toml_paths
    # Use set difference to find extra files that would be covered by a generated REUSE.toml, but were not expected
    unexpected_extra_files = expanded_reuse_toml_paths - expected_reuse_toml_files
    # To determine if all expected files are covered, simply check the length of `missing_files`
    return len(missing_files) == 0, missing_files, unexpected_extra_files
