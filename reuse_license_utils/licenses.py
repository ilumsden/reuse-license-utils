# SPDX-FileCopyrightText: 2026 Ian Lumsden
#
# SPDX-License-Identifier: MIT

import subprocess
from pathlib import Path

from license_expression import ExpressionError, LicenseSymbol, LicenseWithExceptionSymbol, get_spdx_licensing

from reuse_license_utils.utils import get_reuse_command

_licensing = get_spdx_licensing()

SingleLicenseEntry = str | tuple[str, str]


def parse_spdx_identifier(license_id: str) -> list[SingleLicenseEntry]:
    """Parse an SDPX licence identifier into a flat list of license entries.

    This function is used to handle scenarios with complex licensing, such
    as multi-licensing used by projects like Spack or projects using SPDX
    exceptions (e.g., projects using "Apache 2.0 WITH LLVM exceptions").

    Each element of the returned list (i.e., "license entries") can be one
    of the following:
    - A plain string for a standalone license (e.g., MIT)
    - A tuple of license name and exception name for licenses using exceptions (e.g., "Apache 2.0 WITH LLVM exceptions")

    Args:
        license_id (str): An SDPX license identifier (usually specified in the config file).

    Raises:
        ExpressionError: If `license_expression` cannot parse the input.

    Returns:
        A list of license entries containing all the details needed for REUSE to download licenses.
    """
    try:
        parsed_license = _licensing.parse(license_id, validate=True)
    except ExpressionError as e:
        raise ExpressionError(f"Invalid SPDX identifier: {license_id}") from e

    entries = []

    args = parsed_license.args if parsed_license.args else [parsed_license]

    for symbol in args:
        if isinstance(symbol, LicenseWithExceptionSymbol):
            entries.append((symbol.license_symbol.key, symbol.exception_symbol.key))
        elif isinstance(symbol, LicenseSymbol):
            entries.append(symbol.key)

    return entries


def download_licenses(
    repo_root: Path,
    license_ids: list[str],
    use_uv: bool = False,
) -> tuple[set[Path], set[Path], set[Path]]:
    """Download license files with REUSE.

    Args:
        repo_root (Path): The root of the repository to which the license files will be added.
        license_ids (list[str]): The SDPX identifiers of the licenses to download.
        use_uv (bool, optional): If True, invoke REUSE as `uv run reuse` instead of `reuse`. Defaults to False.

    Raises:
        ValueError: If no license IDs are provided.

    Returns:
        A 3-tuple of (0) the set of licenses downloaded, (1) the set of licenses that already exist, and (2) the set of licenses that failed to download.
    """  # noqa: E501
    if not license_ids:
        raise ValueError("No license identifiers provided to `download_licenses`.")

    reuse_cmd = get_reuse_command(use_uv=use_uv)
    downloaded_license_files = set()
    existing_license_files = set()
    failed_license_files = set()

    def download_one_license_or_exception(spdx_id: str) -> None:
        if spdx_id in downloaded_license_files or spdx_id in existing_license_files:
            return
        license_path = repo_root / "LICENSES" / f"{spdx_id}.txt"

        if license_path.exists() and license_path.is_file():
            existing_license_files.add(spdx_id)
            return

        cmd_obj = subprocess.run([*reuse_cmd, "download", spdx_id], cwd=repo_root, check=False)
        if cmd_obj.returncode == 0:
            downloaded_license_files.add(spdx_id)
        else:
            failed_license_files.add(spdx_id)

    for curr_id in license_ids:
        for entry in parse_spdx_identifier(curr_id):
            if isinstance(entry, tuple):
                parsed_id, exception_id = entry
            else:
                parsed_id, exception_id = entry, None
            download_one_license_or_exception(parsed_id)
            if exception_id is not None:
                download_one_license_or_exception(exception_id)

    failed_license_files -= downloaded_license_files | existing_license_files

    return downloaded_license_files, existing_license_files, failed_license_files
