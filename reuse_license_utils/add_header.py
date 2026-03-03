import subprocess
from pathlib import Path

from reuse_license_utils.config import LicenseUtilsConfig
from reuse_license_utils.identify_files import collect_header_files
from reuse_license_utils.utils import _get_reuse_command


def add_headers_to_files(
    files: list[Path],
    year: str,
    copyright_holder: str,
    license_id: str,
    use_uv: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess:
    """Add or update SPDX license headers in the specified files using `reuse addheader`.

    This function is safe to call multiple times on the same files because REUSE updates
    existing headers rather than duplicating them.

    Args:
        files: the files to annotate, relative to the repo root.
        year: the year or year range to include in the header.
        copyright_holder: the copyright holder to include in the header.
        license_id: the SPDX identifier for the license.
        use_uv: if true, invoke reuse with `uv run reuse` instead of just `reuse`.
        check: passed through to the `check` parameter of `subprocess.run`.

    Returns:
        A subprocess.CompletedProcess instance containing information about the invocation of `reuse addheader`.
    """
    if not files:
        raise ValueError("No files provided to `add_headers_to_files`.")

    reuse_cmd = _get_reuse_command(use_uv)

    return subprocess.run(
        [
            *reuse_cmd,
            "addheader",
            "--year",
            year,
            "--copyright",
            copyright_holder,
            "--license",
            license_id,
            *[str(f) for f in files],
        ],
        check=check,
    )


def add_headers_to_group(
    repo_root: Path,
    config: LicenseUtilsConfig,
    group_id: str,
    use_uv: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess:
    """Add or update SPDX license headers in all files specified by a group in the config file.

    Args:
        repo_root: the path to the root of the repo.
        config: the reuse-license-utils config.
        group_id: the ID for the group to which headers should be added.
        use_uv: if true, invoke reuse with `uv run reuse` instead of just `reuse`.
        check: passed through to the `check` parameter of `subprocess.run`.

    Returns:
        A subprocess.CompletedProcess instance containing information about the invocation of `reuse addheader`.
    """
    year = config.header_groups[group_id].copyright_years
    if config.header_groups[group_id].copyright_years is None:
        year = config.default_copyright_years
    if year is None:
        raise ValueError(
            f"Either `default_copyright_years` or the `copyright_years` fields for {group_id} must be provided.",
        )
    copyright_holder = config.header_groups[group_id].copyright_holder
    if config.header_groups[group_id].copyright_holder is None:
        copyright_holder = config.default_copyright_holder
    if copyright_holder is None:
        raise ValueError(
            f"Either `default_copyright_holder` or the `copyright_holder` fields for {group_id} must be provided.",
        )
    license_id = config.header_groups[group_id].license_id
    if config.header_groups[group_id].license_id is None:
        license_id = config.default_license_id
    if license_id is None:
        raise ValueError(
            f"Either `default_license_id` or the `license_id` fields for {group_id} must be provided.",
        )
    return add_headers_to_files(
        files=collect_header_files(repo_root=repo_root, config=config, header_group_id=group_id),
        year=year,
        copyright_holder=copyright_holder,
        license_id=license_id,
        use_uv=use_uv,
        check=check,
    )


def add_headers(repo_root: Path, config: LicenseUtilsConfig, use_uv: bool = False) -> None:
    """Add or update SPDX license headers in all files specified by the config file.

    Args:
        repo_root: the path to the root of the repo.
        config: the reuse-license-utils config.
        use_uv: if true, invoke reuse with `uv run reuse` instead of just `reuse`.

    Returns:
        None

    Raises:
        RuntimeError: If header adding/updating failed.
    """
    failed_groups = set()
    for group_id in config.header_groups.keys():
        completed_process = add_headers_to_group(
            repo_root=repo_root,
            config=config,
            group_id=group_id,
            use_uv=use_uv,
            check=False,
        )
        if completed_process.returncode != 0:
            failed_groups.add(group_id)
    if len(failed_groups) > 0:
        failed_group_list = "\n".join([f"  - {group_id}" for group_id in sorted(failed_groups)])
        raise RuntimeError(
            f"Failed to add or update some of files requested in the config.\nThe following groups failed:\n{failed_group_list}",  # noqa: E501
        )
