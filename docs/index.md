# zoo-runner-common

Welcome to the documentation for **zoo-runner-common**, a Python package providing common base classes and utilities for implementing CWL runners in the ZOO-Project ecosystem.

## Overview

This package provides the foundational `BaseRunner` class and utilities that are used by specific runner implementations (Calrissian, Argo Workflows, WES, etc.).

## Key Components

- **BaseRunner**: Abstract base class for CWL runners
    - Standard interface for runner implementations
    - Configuration management
    - Process lifecycle management
    - Error handling

- **ZooConf**: Configuration parser for ZOO-Project
    - Parse ZOO configuration files
    - Extract inputs/outputs
    - Handle data types

- **ZooStub**: Testing stub for ZOO module
    - Mock ZOO module for development and testing
    - Service status codes

## Architecture

```
zoo-runner-common (base package)
    ├── BaseRunner (abstract)
    │
    ├── zoo-calrissian-runner
    │   └── ZooCalrissianRunner extends BaseRunner
    │
    ├── zoo-argowf-runner
    │   └── ZooArgoWorkflowsRunner extends BaseRunner
    │
    └── zoo-wes-runner
        └── ZooWESRunner extends BaseRunner
```

## Quick Example

```python
from base_runner import BaseRunner

class MyRunner(BaseRunner):
    def execute(self):
        """Implement execution logic"""
        # Your runner implementation
        pass
```

## Runner Implementations

- **zoo-calrissian-runner**: Kubernetes-based runner using Calrissian
- **zoo-argowf-runner**: Argo Workflows-based runner
- **zoo-wes-runner**: GA4GH WES API-based runner

## Installation

```bash
pip install zoo-runner-common
```

## Next Steps

- [Quick Start Guide](getting-started/quickstart.md)
- [Implementing a New Runner](development/implementing-runners.md)
- [API Reference](api/base-runner.md)
