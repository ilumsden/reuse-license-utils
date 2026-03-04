# SPDX-FileCopyrightText: 2026 Ian Lumsden
#
# SPDX-License-Identifier: MIT

import warnings
from pathlib import Path
from typing import Any

from reuse_license_utils.config import LicenseUtilsConfig
from reuse_license_utils.verify import verify_reuse_toml_paths


def generate_reuse_toml(repo_root: Path, config: LicenseUtilsConfig) -> dict[str, Any]:
    """Generate the contents of a REUSE.toml based on the config.

    Args:
        repo_root (Path): The path to the repository root.
        config (LicenseUtilsConfig): The reuse-license-utils config.

    Raises:
        ValueError: When there is neither a specific copyright holder, copyright year, or license ID nor a default one for an entry under `reuse_toml_paths` in the config.

    Returns:
        The contents of the generated REUSE.toml file.
    """  # noqa: E501
    # Check if the config covers all expected files and any extra files
    covers_expected_files, missing_files, unexpected_extra_files = verify_reuse_toml_paths(repo_root, config)
    # If the config does not cover all expected files, produce a warning to inform them that they should probably
    # fix the config
    if not covers_expected_files:
        warning_msg = (
            "The config for reuse-license-utils will produce a REUSE.toml that does not cover all expected files.\n"
            "The following files would not be covered by REUSE.toml:\n"
        )
        warning_msg += "\n".join(f"  - {mfile}" for mfile in missing_files)
        warning_msg += (
            "\nEither update the REUSE.toml by hand to include these files or reconfigure reuse-license-utils."
        )
        warnings.warn(warning_msg, RuntimeWarning)
    # If the config covers files that were not expected to be covered by REUSE.toml, produce a warning that informs
    # users that this could cause issues
    if len(unexpected_extra_files) > 0:
        warning_msg = (
            "The config for reuse-license-utils will produce a REUSE.toml that covers more files than expected.\n"
            "The following extra files would be covered by REUSE.toml:\n"
        )
        warning_msg += "\n".join(f"  - {efile}" for efile in unexpected_extra_files)
        warning_msg += "\nThis is not necessarily a problem, but it may cause issues with REUSE tooling."
        warnings.warn(warning_msg, RuntimeWarning)
    # Create a JSON-/TOML-compatible object for the config
    data = {
        "version": 1,
        "annotations": [],
    }

    # Add entries for each entry in the config's `reuse_toml_paths` section
    for path_config in config.reuse_toml_paths:
        # Get and verify the copyright holder
        copyright_holder = path_config.copyright_holder
        if path_config.copyright_holder is None:
            copyright_holder = config.default_copyright_holder
        if copyright_holder is None:
            raise ValueError(
                "Either the `default_copyright_holder` or the `copyright_holder` field for the REUSE.toml configuration must be provided.",  # noqa: E501
            )
        # Get and verify the copyright years
        copyright_years = path_config.copyright_years
        if path_config.copyright_years is None:
            copyright_years = config.default_copyright_years
        if copyright_years is None:
            raise ValueError(
                "Either the `default_copyright_years` or the `copyright_years` field for the REUSE.toml configuration must be provided.",  # noqa: E501
            )
        # Get and verify the license ID
        license_id = path_config.license_id
        if path_config.license_id is None:
            license_id = config.default_license_id
        if license_id is None:
            raise ValueError(
                "Either the `default_license_id` or the `license_id` field for the REUSE.toml configuration must be provided.",  # noqa: E501
            )
        # Create the entry for this path
        data["annotations"].append(
            {
                "path": path_config.path,
                "SPDX-FileCopyrightText": f"{copyright_years} {copyright_holder}",
                "SPDX-License-Identifier": license_id,
            },
        )

    return data
