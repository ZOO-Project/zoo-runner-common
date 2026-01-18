# Installation

## Requirements

- Python 3.8 or higher
- pip package manager

## From PyPI

```bash
pip install zoo-runner-common
```

## From Source

```bash
git clone https://github.com/ZOO-Project/zoo-runner-common.git
cd zoo-runner-common
pip install .
```

## Development Installation

For contributing or development:

```bash
git clone https://github.com/ZOO-Project/zoo-runner-common.git
cd zoo-runner-common
pip install -e .
```

This installs the package in editable mode with development dependencies.

## Verification

Verify the installation:

```python
from base_runner import BaseRunner
print("zoo-runner-common installed successfully!")
```

## Next Steps

- [Quick Start Guide](quickstart.md)
- [Implementing a Runner](../development/implementing-runners.md)
