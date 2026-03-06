# Configuration

`reuse-license-utils` is configured via a `[tool.reuse-license-utils]` section
in your `pyproject.toml`.

## Example
```toml
[tool.reuse-license-utils]
default_copyright_holder = "Global Computing Lab"
default_copyright_years = "2026"
default_license_id = "Apache-2.0 WITH LLVM-exception"

[tool.reuse-license-utils.header_groups.source]
include_patterns = [
    "**/*.py",
    "**/*.cpp",
    "**/*.h",
]
exclude_patterns = [
    "src/generated/**",
]

[[tool.reuse-license-utils.reuse_toml_paths]]
path = "README.md"

[[tool.reuse-license-utils.reuse_toml_paths]]
path = ".github/**/*"
```

## Reference

See the {py:class}`~reuse_license_utils.config.LicenseUtilsConfig` API docs for
the full list of configuration fields.