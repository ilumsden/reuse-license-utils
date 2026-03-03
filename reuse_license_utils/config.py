from pathlib import Path

from pydantic import BaseModel

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError as e:
        raise ImportError("'tomllib' or 'tomli' is required!") from e


# Files starting with any of the following are ignored by REUSE
REUSE_EXEMPT_PREFIXES: list[str] = [
    "COPYING",
    "LICENSE",
    "LICENCE",
]

# Files in the following directories are ignored by REUSE
REUSE_EXEMPT_DIRS: list[str] = [
    ".git",
    "LICENSES",
    ".reuse",
]


class HeadersConfig(BaseModel):
    """Configuration for header generation/update."""

    include_patterns: list[str]
    """A list of glob patterns specifying files to which headers should be applied."""

    exclude_patterns: list[str] = []
    """A list of glob patterns specifying files to which headers should **not** be applied."""

    copyright_holder: str | None = None
    """The name of the copyright holder (e.g., "Global Computing Lab")."""

    copyright_years: str | None = None
    """The year or year range for the copyright (e.g., "2025-2026")."""

    license_id: str | None = None
    """The SPDX identifier for the license (e.g., "Apache-2.0 WITH LLVM-exception")."""


class ReuseTomlGenerationPatternConfig(BaseModel):
    """Configuration for a single path in the generation of REUSE.toml"""

    path: str
    """The path or glob to add to REUSE.toml."""

    copyright_holder: str | None = None
    """The name of the copyright holder (e.g., "Global Computing Lab")."""

    copyright_years: str | None = None
    """The year or year range for the copyright (e.g., "2025-2026")."""

    license_id: str | None = None
    """The SPDX identifier for the license."""


class LicenseUtilsConfig(BaseModel):
    """Configuration for reuse-license-utils."""

    default_copyright_holder: str | None = None
    """The default copyright holder to use when not specified in other parts of the config."""

    default_copyright_years: str | None = None
    """The default copyright year or year range to use when not specified in other parts of the config."""

    default_license_id: str | None = None
    """The SPDX identifier for the default license to use when not specified in other parts of the config."""

    header_groups: dict[str, HeadersConfig]
    """Configuration for header generation/update."""

    reuse_toml_paths: list[ReuseTomlGenerationPatternConfig] = []
    """Specification of paths that will be included in REUSE.toml."""


def load_config(config_path: Path) -> LicenseUtilsConfig:
    local_config_path = config_path.expanduser().resolve()
    if not local_config_path.exists():
        raise FileNotFoundError(f"Config file could not be found at {config_path!s}")

    with local_config_path.open("rb") as f:
        config_data = tomllib.load(f)

    if local_config_path.name == "pyproject.toml":
        config_data = config_data.get("tool", {}).get("reuse-license-utils")

    if not config_data:
        raise KeyError(
            f"There is no config data in {config_path!s}. Keep in mind that we check in [tool.reuse-license-utils] if the file is 'pyproject.toml'.",  # noqa: E501
        )
    return LicenseUtilsConfig(**config_data)
