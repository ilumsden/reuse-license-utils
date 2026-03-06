# CLI Reference

All commands are available via the `reuse-license-utils` CLI.

## `add-headers`

Adds or updates SPDX license headers in source files.
```bash
reuse-license-utils add-headers [-r REPO_ROOT] [-c CONFIG_FILE] [-u]
```

## `generate-toml`

Generates a `REUSE.toml` file from `reuse_toml_paths` in the config.
```bash
reuse-license-utils generate-toml [-r REPO_ROOT] [-c CONFIG_FILE] [-f REUSE_TOML_FILE]
```

## `download-licenses`

Downloads license texts into `LICENSES/`.
```bash
reuse-license-utils download-licenses [-r REPO_ROOT] [-c CONFIG_FILE] [-u]
```

## `verify`

Verifies REUSE compliance via `reuse lint`.
```bash
reuse-license-utils verify [-r REPO_ROOT] [-c CONFIG_FILE] [-u] [-q]
```