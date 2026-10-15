# Contributing to zoo-runner-common

Thank you for your interest in contributing to `zoo-runner-common`! This document provides guidelines for contributing to the project.

## Overview

`zoo-runner-common` provides shared utilities for ZOO-Project CWL runners, including `BaseRunner`, `ExecutionHandler`, `ZooConf`, `ZooInputs`, `ZooOutputs`, and `ZooStub`. The project uses [Hatch](https://hatch.pypa.io/) as its build and development tool.

---

> **Important:** Always open your Pull Request against the `develop` branch, **not** `main`.
> Pull Requests targeting `main` directly will not be accepted.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- [Hatch](https://hatch.pypa.io/latest/install/) (`pip install hatch`)

### Development Setup

1. **Fork and Clone**

   ```bash
   git clone https://github.com/ZOO-Project/zoo-runner-common.git
   cd zoo-runner-common
   ```

2. **Install Hatch**

   ```bash
   pip install hatch
   ```

3. **Enter the Default Development Environment**

   Hatch automatically creates and manages a virtual environment for you:

   ```bash
   hatch shell
   ```

   This installs all dependencies defined under `[tool.hatch.envs.default]` in `pyproject.toml`.

5. **Verify Installation**

   ```bash
   python -c "from zoo_runner_common import BaseRunner; print('OK')"
   ```

---

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Use these prefixes:

- `feature/` — New features
- `fix/` — Bug fixes
- `docs/` — Documentation updates
- `refactor/` — Code refactoring
- `test/` — Test additions or fixes

### 2. Make Changes

Follow the coding standards described in the [Code Standards](#code-standards) section below.

### 3. Run Tests

The project uses `pytest` for testing via a dedicated Hatch environment:

```bash
# Run tests
hatch run test:test

# Run tests quietly
hatch run test:test-q
```

### 4. Update Documentation

- Update docstrings in the source code
- Update relevant `.md` files in `docs/`, if present

### 5. Commit Changes

Write clear, conventional commit messages:

```bash
git add .
git commit -m "feat: add new shared utility method to BaseRunner"
```

Commit types:

- `feat` — New feature
- `fix` — Bug fix
- `docs` — Documentation only
- `style` — Formatting, no logic change
- `refactor` — Code restructuring
- `test` — Adding or updating tests
- `chore` — Maintenance, dependency updates

### 6. Push and Create a Pull Request

```bash
git push origin feature/your-feature-name
```

Then open a Pull Request on GitHub with:

- **Base branch set to `develop`** — this is required
- A clear title and description
- Reference to any related issues (`Closes #123`)
- A summary of what changed and why
- Notes on any breaking changes

> **Reminder:** The base branch of your PR must be `develop`, not `main`.
> `main` is only updated by maintainers when cutting a release from `develop`.

---

## Hatch Environments

The project defines two Hatch environments in `pyproject.toml`:

| Environment | Purpose | Key Command |
|---|---|---|
| `default` | Day-to-day development | `hatch shell` |
| `test` | Running tests | `hatch run test:test` |

---

## Code Standards

### Python Style

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use **type hints** on all public methods
- Use **Google-style docstrings**
- Minimum Python version: **3.10**

**Good example:**

```python
def get_workflow_id(self) -> str:
    """
    Return the workflow identifier from the ZOO configuration.

    Returns:
        The workflow ID string.

    Raises:
        ValueError: If the workflow ID is not set.
    """
    if not self._workflow_id:
        raise ValueError("Workflow ID is not set")
    return self._workflow_id
```

### Error Handling

Catch specific exceptions and use structured logging via `loguru`:

```python
from loguru import logger

def load_config(self, path: str) -> dict:
    """Load configuration from a YAML file."""
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.warning(f"Config file not found: {path}")
        return {}
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in {path}: {e}")
        raise
```

### Versioning

The package version is managed in `zoo_runner_common/__about__.py`. Do **not** manually edit the version; it is updated as part of the release process.

---

## Testing Guidelines

Place unit tests under `tests/` and name files `test_*.py`:

```python
# tests/test_base_runner.py
import unittest
from zoo_runner_common import BaseRunner

class TestBaseRunner(unittest.TestCase):

    def test_initialization(self):
        """Test that BaseRunner initializes correctly."""
        self.assertIsNotNone(BaseRunner)
```

---

## Release Process

Releases are managed by project maintainers:

1. Ensure all changes are merged into `develop` and tested
2. Update the version in `zoo_runner_common/__about__.py`
3. Update `CHANGELOG.md`
4. Merge `develop` into `main`
5. Create and push a release tag:

   ```bash
   git tag v0.1.4
   git push origin v0.1.4
   ```

6. Build and publish the package:

   ```bash
   hatch build
   hatch publish
   ```

---

## Getting Help

- **Bug reports / feature requests**: [Open an issue](https://github.com/ZOO-Project/zoo-runner-common/issues)
- **Contact**: Email the maintainers

---

## Code of Conduct

We are committed to a welcoming and inclusive environment. When participating:

- Be respectful of differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the project and community
- Show empathy towards other contributors

---

## License

By contributing, you agree that your contributions will be licensed under the **Apache License 2.0**, the same license as this project.

---

Thank you for contributing! 🎉
