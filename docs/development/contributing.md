# Contributing to zoo-runner-common

Thank you for your interest in contributing to zoo-runner-common!

## Getting Started

### Prerequisites

- Python 3.8+
- Git

### Setup

```bash
git clone https://github.com/ZOO-Project/zoo-runner-common.git
cd zoo-runner-common
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature
```

### 2. Make Changes

Follow coding standards:

```python
# Good
class MyRunner(BaseRunner):
    """
    My custom runner implementation.
    
    This runner executes CWL workflows using [backend].
    """
    
    def execute(self):
        """Execute workflow with error handling"""
        try:
            prepared = self.prepare()
            result = self.run_workflow(prepared.cwl)
            self.finalize(None, result, None, None)
            return zoo.SERVICE_SUCCEEDED
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return zoo.SERVICE_FAILED
```

### 3. Write Tests

```python
# tests/test_myrunner.py
def test_runner_execution():
    """Test runner execution"""
    runner = MyRunner(cwl, inputs, conf, outputs)
    status = runner.execute()
    assert status == zoo.SERVICE_SUCCEEDED
```

Run tests:

```bash
pytest tests/
```

### 4. Update Documentation

- Add docstrings
- Update relevant docs in `docs/`
- Add examples

### 5. Commit and Push

```bash
git add .
git commit -m "feat: add new feature"
git push origin feature/your-feature
```

### 6. Create Pull Request

Create PR on GitHub with:
- Clear description
- Related issues
- Test results

## Code Standards

### Python Style

- Follow PEP 8
- Use type hints
- Write docstrings

```python
def my_method(self, param: str) -> bool:
    """
    Short description.
    
    Args:
        param: Parameter description
    
    Returns:
        True if successful
    """
    pass
```

### Testing

- Write unit tests
- Aim for >80% coverage
- Test error cases

## Documentation

### Docstrings

Use Google style:

```python
def prepare(self):
    """
    Prepare for execution.
    
    This method calls the pre-execution hook and wraps
    the CWL workflow with staging steps.
    
    Returns:
        SimpleNamespace with 'cwl' and 'params' attributes
    
    Raises:
        Exception: If pre-execution hook fails
    """
    pass
```

## Questions?

- Open an issue
- Start a discussion
- Contact maintainers

Thank you for contributing! 🎉
