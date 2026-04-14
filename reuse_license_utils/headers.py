# SPDX-FileCopyrightText: 2026 Ian Lumsden
#
# SPDX-License-Identifier: MIT

import re
import subprocess
from pathlib import Path

from reuse_license_utils.config import LicenseUtilsConfig
from reuse_license_utils.files import collect_header_files
from reuse_license_utils.utils import get_reuse_command


def strip_copyright_lines(
    files: list[Path],
    copyright_holder: str,
) -> None:
    """Remove existing SPDX-FileCopyrightText lines matching the given copyright holder.

    This function allow `reuse annotate` to add updated copyright lines to files
    without duplicating old ones.

    Args:
        files (list[Path]): The list of files to process.
        copyright_holder (str): The copyright holder to match against (e.g., "Global Computing Lab").
    """
    # Breakdown of regex:
    #   * "^.+"": matches the comment character and any spaces at the start of the line
    #   * "SPDX-FileCopyrightText:": matches that literal SPDX tag
    #   * ".*": match all text between the tag and the copyright holder (namely the year or year range)
    #   * "re.escape(copyright_holder)": escapes the copyright holder name in case it contains regex special characters
    #   * ".*$": matches everything between the copyright holder name and the end of the line
    #   * "\n": matches the newline so that no blank lines are left behind
    #   * re.MULTILINE: makes "^" and "$" match the start and end of each line
    pattern = re.compile(
        r"^.+SPDX-FileCopyrightText:.*" + re.escape(copyright_holder) + r".*$\n?",
        re.MULTILINE,
    )

    for file in files:
        # Read the contents of the current file
        original = file.read_text(encoding="utf-8")
        # Apply the regex and replace all matches with empty strings
        updated = pattern.sub("", original)
        # Only overwrite the original file if there was text that matched the regex
        if updated != original:
            # Define a temporary file to save the contents without the copyright lines
            tmp_path = file.with_suffix(file.suffix + ".tmp")
            try:
                # Write the contents w/o copyright lines to the temp file
                with tmp_path.open("w", encoding="utf-8") as f:
                    f.write(updated)
                # If the contents were written successfully, rename the temp file to
                # the original file's name to overwrite the original file
                tmp_path.rename(file)
            # If anything in the writing process failed, delete the temp file, and
            # then re-raise the exception
            except Exception:
                tmp_path.unlink(missing_ok=True)
                raise


def add_headers_to_files(
    files: list[Path],
    year: str,
    copyright_holder: str,
    license_id: str,
    style: str | None = None,
    use_uv: bool = False,
    check: bool = True,
    overwrite_copyright_lines: bool = False,
) -> subprocess.CompletedProcess:
    """Add or update SPDX license headers in the specified files using `reuse annotate`.

    This function is safe to call multiple times on the same files because REUSE updates
    existing headers rather than duplicating them.

    Args:
        files: The files to annotate, relative to the repo root.
        year: The year or year range to include in the header.
        copyright_holder: The copyright holder to include in the header.
        license_id: The SPDX identifier for the license.
        style: The style to use for formatting the license headers in the file(s).
        use_uv: If true, invoke reuse with `uv run reuse` instead of just `reuse`. Defaults to False.
        check: Passed through to the `check` parameter of `subprocess.run`. Defaults to True.
        overwrite_copyright_lines: If True, use `strip_copyright_lines` to override copyright lines. Defaults to False.

    Returns:
        A subprocess.CompletedProcess instance containing information about the invocation of `reuse annotate`.
    """
    if not files:
        raise ValueError("No files provided to `add_headers_to_files`.")

    if overwrite_copyright_lines:
        strip_copyright_lines(files=files, copyright_holder=copyright_holder)

    reuse_cmd = get_reuse_command(use_uv)

    full_cmd = [
        *reuse_cmd,
        "annotate",
        "--year",
        year,
        "--copyright",
        copyright_holder,
        "--license",
        license_id,
    ]
    if style is not None:
        full_cmd.extend(["--style", style])
    full_cmd.extend([str(f) for f in files])

    return subprocess.run(
        full_cmd,
        check=check,
    )


def add_headers_to_group(
    repo_root: Path,
    config: LicenseUtilsConfig,
    group_id: str,
    use_uv: bool = False,
    check: bool = True,
    overwrite_copyright_lines: bool = False,
) -> subprocess.CompletedProcess:
    """Add or update SPDX license headers in all files specified by a group in the config file.

    Args:
        repo_root: The path to the root of the repo.
        config: The reuse-license-utils config.
        group_id: The ID for the group to which headers should be added.
        use_uv: If true, invoke reuse with `uv run reuse` instead of just `reuse`.
        check: passed through to the `check` parameter of `subprocess.run`.
        overwrite_copyright_lines: If True, use `strip_copyright_lines` to override copyright lines. Defaults to False.

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
        style=config.header_groups[group_id].style,
        use_uv=use_uv,
        check=check,
        overwrite_copyright_lines=overwrite_copyright_lines,
    )


def add_headers(
    repo_root: Path,
    config: LicenseUtilsConfig,
    use_uv: bool = False,
    overwrite_copyright_lines: bool = False,
) -> None:
    """Add or update SPDX license headers in all files specified by the config file.

    Args:
        repo_root: the path to the root of the repo.
        config: the reuse-license-utils config.
        use_uv: if true, invoke reuse with `uv run reuse` instead of just `reuse`.
        overwrite_copyright_lines: If True, use `strip_copyright_lines` to override copyright lines. Defaults to False.

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
            overwrite_copyright_lines=overwrite_copyright_lines,
        )
        if completed_process.returncode != 0:
            failed_groups.add(group_id)
    if len(failed_groups) > 0:
        failed_group_list = "\n".join([f"  - {group_id}" for group_id in sorted(failed_groups)])
        raise RuntimeError(
            f"Failed to add or update some of files requested in the config.\nThe following groups failed:\n{failed_group_list}",  # noqa: E501
        )
