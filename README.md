# reuse-license-utils

A command-line tool and Python library for managing [REUSE](https://reuse.software/)-compliant
license headers and metadata in Python and C++ projects.

## Overview

`reuse-license-utils` automates the most tedious parts of achieving and maintaining
[REUSE spec](https://reuse.software/spec/) compliance in your repository:

- Adding and updating SPDX license headers in source files
- Generating a `REUSE.toml` file for files that cannot carry inline headers
- Downloading license texts into the `LICENSES/` directory
- Verifying that your repository is fully REUSE-compliant

## Requirements

- Python 3.10 or later
- [REUSE](https://github.com/fsfe/reuse-tool) (`pip install reuse`)
- A Git repository

## Installation

```bash
pip install reuse-license-utils
```

## Configuration

`reuse-license-utils` reads its configuration from a `[tool.reuse-license-utils]` section
in your `pyproject.toml`, or from a standalone TOML config file passed via `--config-file`.

### Top-level fields

These fields set defaults that apply across all header groups and `REUSE.toml` path
entries. Any of them can be overridden at the group or path level.

| Field                      | Type   | Description                                                                                                                                           |
| -------------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `default_copyright_holder` | `str`  | Default copyright holder, e.g. `"Global Computing Lab"`.                                                                                              |
| `default_copyright_years`  | `str`  | Default copyright year or range, e.g. `"2025"` or `"2024-2026"`.                                                                                      |
| `default_license_id`       | `str`  | Default SPDX license expression, e.g. `"Apache-2.0 WITH LLVM-exception"`. Supports the full SPDX grammar including `WITH`, `AND`, and `OR` operators. |
| `header_groups`            | `dict` | Named groups of source files to annotate with inline SPDX headers. See [Header groups](#header-groups) below.                                         |
| `reuse_toml_paths`         | `list` | Path entries to declare in the generated `REUSE.toml`. See [REUSE.toml paths](#reusetoml-paths) below.                                                |

### Header groups

`header_groups` is a dictionary of named groups, each configuring a set of source
files to annotate. This allows different parts of your codebase to have different
copyright holders, years, or licenses if needed.

| Field              | Type        | Description                                                                                 |
| ------------------ | ----------- | ------------------------------------------------------------------------------------------- |
| `include_patterns` | `list[str]` | **Required.** Glob patterns for files to annotate. Supports `**` for recursive matching.    |
| `exclude_patterns` | `list[str]` | Glob patterns for files to exclude. Supports `**` for recursive matching. Defaults to `[]`. |
| `copyright_holder` | `str`       | Overrides `default_copyright_holder` for this group.                                        |
| `copyright_years`  | `str`       | Overrides `default_copyright_years` for this group.                                         |
| `license_id`       | `str`       | Overrides `default_license_id` for this group.                                              |

### REUSE.toml paths

`reuse_toml_paths` is a list of entries declaring licensing information for files
that cannot carry inline SPDX headers (e.g. `README.md`, `.gitignore`, CI config).
Each entry corresponds to one `[[annotations]]` block in the generated `REUSE.toml`.

| Field              | Type  | Description                                            |
| ------------------ | ----- | ------------------------------------------------------ |
| `path`             | `str` | **Required.** Path or glob to declare in `REUSE.toml`. |
| `copyright_holder` | `str` | Overrides `default_copyright_holder` for this entry.   |
| `copyright_years`  | `str` | Overrides `default_copyright_years` for this entry.    |
| `license_id`       | `str` | Overrides `default_license_id` for this entry.         |

### Example

```toml
[tool.reuse-license-utils]
default_copyright_holder = "Global Computing Lab"
default_copyright_years = "2026"
default_license_id = "Apache-2.0 WITH LLVM-exception"

[tool.reuse-license-utils.header_groups.source]
include_patterns = [
    "**/*.py",
    "**/*.cpp",
    "**/*.c",
    "**/*.h",
    "**/*.hpp",
    "**/*.cxx",
]
exclude_patterns = [
    "src/generated/**",
]

[[tool.reuse-license-utils.reuse_toml_paths]]
path = "README.md"

[[tool.reuse-license-utils.reuse_toml_paths]]
path = "pyproject.toml"

[[tool.reuse-license-utils.reuse_toml_paths]]
path = ".gitignore"

[[tool.reuse-license-utils.reuse_toml_paths]]
path = ".github/**"
```

In this example, all entries inherit `default_copyright_holder`, `default_copyright_years`,
and `default_license_id`. To override for a specific entry:

```toml
[[tool.reuse-license-utils.reuse_toml_paths]]
path = "third_party/**"
copyright_holder = "Some Other Author"
copyright_years = "2023"
license_id = "MIT"
```

## Usage

All commands are available via the `reuse-license-utils` CLI. Every subcommand
accepts `--repo-root` and `--config-file` options to override the autodetected
repository root and config file location respectively.

```
usage: reuse-license-utils [-h]
                           {generate-toml,add-headers,download-licenses,verify}
                           ...
```

### `add-headers`

Adds or updates SPDX license headers in all source files matched by each group's
`include_patterns`. Safe to run multiple times — existing headers are updated
rather than duplicated.

```bash
reuse-license-utils add-headers [-r REPO_ROOT] [-c CONFIG_FILE] [-u]
```

| Option                      | Short | Description                                                                        |
| --------------------------- | ----- | ---------------------------------------------------------------------------------- |
| `--repo-root REPO_ROOT`     | `-r`  | Path to the repository root. If not provided, autodetected via GitPython.          |
| `--config-file CONFIG_FILE` | `-c`  | Path to the config file. If not provided, uses `pyproject.toml` under `repo-root`. |
| `--use-uv`                  | `-u`  | Invoke REUSE using `uv` instead of invoking directly.                              |

### `generate-toml`

Generates a `REUSE.toml` file from the `reuse_toml_paths` entries in the config.

```bash
reuse-license-utils generate-toml [-r REPO_ROOT] [-c CONFIG_FILE] [-f REUSE_TOML_FILE]
```

| Option                              | Short | Description                                                                        |
| ----------------------------------- | ----- | ---------------------------------------------------------------------------------- |
| `--repo-root REPO_ROOT`             | `-r`  | Path to the repository root. If not provided, autodetected via GitPython.          |
| `--config-file CONFIG_FILE`         | `-c`  | Path to the config file. If not provided, uses `pyproject.toml` under `repo-root`. |
| `--reuse-toml-file REUSE_TOML_FILE` | `-f`  | Path to the `REUSE.toml` file to generate. Defaults to `<repo_root>/REUSE.toml`.   |

### `download-licenses`

Downloads license texts for all licenses referenced in `default_license_id` and
any group- or path-level `license_id` overrides into the `LICENSES/` directory
using `reuse download`. Compound SPDX expressions (e.g. `Apache-2.0 WITH LLVM-exception`)
are handled by downloading the base license. A warning is printed for any exceptions,
indicating which file should be updated manually.

```bash
reuse-license-utils download-licenses [-r REPO_ROOT] [-c CONFIG_FILE] [-u]
```

| Option                      | Short | Description                                                                        |
| --------------------------- | ----- | ---------------------------------------------------------------------------------- |
| `--repo-root REPO_ROOT`     | `-r`  | Path to the repository root. If not provided, autodetected via GitPython.          |
| `--config-file CONFIG_FILE` | `-c`  | Path to the config file. If not provided, uses `pyproject.toml` under `repo-root`. |
| `--use-uv`                  | `-u`  | Invoke REUSE using `uv` instead of invoking directly.                              |

### `verify`

Verifies that the repository is fully REUSE-compliant by running `reuse lint`.
Exits with a non-zero status if any files are missing licensing information, making
it suitable for use in CI pipelines.

```bash
reuse-license-utils verify [-r REPO_ROOT] [-c CONFIG_FILE] [-u] [-q]
```

| Option                      | Short | Description                                                                        |
| --------------------------- | ----- | ---------------------------------------------------------------------------------- |
| `--repo-root REPO_ROOT`     | `-r`  | Path to the repository root. If not provided, autodetected via GitPython.          |
| `--config-file CONFIG_FILE` | `-c`  | Path to the config file. If not provided, uses `pyproject.toml` under `repo-root`. |
| `--use-uv`                  | `-u`  | Invoke REUSE using `uv` instead of invoking directly.                              |
| `--quiet`                   | `-q`  | Pass `--quiet` to `reuse lint`.                                                    |

## Typical Workflow

```bash
# 1. Add [tool.reuse-license-utils] config to pyproject.toml

# 2. Download the license text into LICENSES/
reuse-license-utils download-licenses

# 3. Add SPDX headers to all source files
reuse-license-utils add-headers

# 4. Generate REUSE.toml for non-source files
reuse-license-utils generate-toml

# 5. Verify compliance
reuse-license-utils verify
```

## CI Integration

Add a verification step to your GitHub Actions workflow:

```yaml
name: REUSE Compliance

on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install reuse-license-utils
      - run: reuse-license-utils verify --quiet
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.