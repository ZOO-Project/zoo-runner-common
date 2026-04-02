# Installation

## Requirements

- Python 3.10 or higher
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

## Development Workflow with Hatch

For development and test execution:

```bash
git clone https://github.com/ZOO-Project/zoo-runner-common.git
cd zoo-runner-common
pip install hatch
hatch run test
```

To build the package locally:

```bash
hatch build
```

## Verification

Verify the installation:

```python
from zoo_runner_common import BaseRunner
print("zoo-runner-common installed successfully!")
```

## Next Steps

- [Quick Start Guide](quickstart.md)
- [Implementing a Runner](../development/implementing-runners.md)
