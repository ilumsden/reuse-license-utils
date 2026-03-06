# Getting Started

## Requirements

- Python 3.10 or later
- A Git repository

## Installation
```bash
pip install reuse-license-utils
```

## Typical workflow
```bash
# 1. Add [tool.reuse-license-utils] config to pyproject.toml

# 2. Download license texts into LICENSES/
reuse-license-utils download-licenses

# 3. Add SPDX headers to all source files
reuse-license-utils add-headers

# 4. Generate REUSE.toml for non-source files
reuse-license-utils generate-toml

# 5. Verify compliance
reuse-license-utils verify
```