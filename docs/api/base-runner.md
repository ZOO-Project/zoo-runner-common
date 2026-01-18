# BaseRunner API Reference

::: base_runner.BaseRunner
    options:
      show_source: true
      show_root_heading: true
      heading_level: 2

## Class Overview

`BaseRunner` is the abstract base class for implementing CWL workflow runners in ZOO-Project.

## Constructor

```python
def __init__(self, cwl, inputs, conf, outputs, execution_handler=None)
```

**Parameters:**

- `cwl`: CWL workflow definition (path or content)
- `inputs`: ZOO inputs dictionary
- `conf`: ZOO configuration dictionary
- `outputs`: ZOO outputs dictionary
- `execution_handler`: Optional execution handler instance (e.g., `CommonExecutionHandler`)

## Abstract Methods

Subclasses must implement these methods:

### execute()

Execute the CWL workflow.

```python
@abstractmethod
def execute(self):
    """Execute the workflow"""
    pass
```

### wrap()

Wrap the CWL workflow with stage-in/stage-out steps.

```python
@abstractmethod
def wrap(self):
    """Wrap workflow with staging steps"""
    pass
```

### get_processing_parameters()

Get processing parameters specific to the runner.

```python
@abstractmethod
def get_processing_parameters(self):
    """Get runner-specific parameters"""
    pass
```

## Methods

### prepare()

Shared pre-execution logic.

```python
def prepare(self)
```

**Behavior:**

1. Logs execution start
2. Updates status to 2%
3. Calls `execution_handler.pre_execution_hook()`
4. Wraps CWL workflow
5. Prepares processing parameters

**Returns:**
- SimpleNamespace with:
  - `cwl`: Wrapped workflow
  - `params`: Processing parameters

**Example:**

```python
prepared = runner.prepare()
wrapped_cwl = prepared.cwl
params = prepared.params
```

### finalize()

Finalization logic after execution.

```python
def finalize(self, log, output, usage_report, tool_logs)
```

**Parameters:**

- `log`: Execution log
- `output`: Workflow outputs
- `usage_report`: Resource usage statistics
- `tool_logs`: Tool execution logs

**Behavior:**

1. Calls `execution_handler.post_execution_hook()`
2. Calls `execution_handler.handle_outputs()`

**Example:**

```python
runner.finalize(log, outputs, usage, tool_logs)
```

### update_status()

Update execution status in ZOO.

```python
def update_status(self, progress: int, message: str = "")
```

**Parameters:**

- `progress` (int): Progress percentage (0-100)
- `message` (str): Status message

**Example:**

```python
runner.update_status(50, "Processing data...")
```

### validate_inputs()

Validate input parameters.

```python
def validate_inputs(self) -> bool
```

**Returns:**
- bool: True if inputs are valid

**Example:**

```python
if not runner.validate_inputs():
    return zoo.SERVICE_FAILED
```

### log_output()

Log output information.

```python
def log_output(self, output)
```

**Parameters:**

- `output`: Output data to log

### get_namespace_name()

Get or generate namespace name for execution.

```python
def get_namespace_name(self) -> str
```

**Returns:**
- str: Namespace name (format: `{identifier}-{usid}`)

**Example:**

```python
namespace = runner.get_namespace_name()
# Returns: "process-name-12345"
```

## Attributes

### cwl
CWL workflow definition.

### inputs  
ZOO inputs dictionary.

### conf
ZOO configuration dictionary.

### outputs
ZOO outputs dictionary.

### execution_handler
Execution handler instance.

### namespace_name
Kubernetes namespace name.

### zoo_conf
SimpleNamespace wrapper for configuration.

## Default Handler

If no execution handler is provided, BaseRunner creates a default handler with no-op methods:

```python
class DefaultHandler:
    def pre_execution_hook(self):
        pass
    
    def post_execution_hook(self, *args, **kwargs):
        pass
    
    def get_secrets(self):
        return None
    
    def get_additional_parameters(self):
        return {}
    
    def get_pod_env_vars(self):
        return None
    
    def get_pod_node_selector(self):
        return None
    
    def handle_outputs(self, *args, **kwargs):
        pass
    
    def set_job_id(self, job_id):
        pass
```

## Usage Pattern

```python
from base_runner import BaseRunner

class MyRunner(BaseRunner):
    def execute(self):
        """Execute workflow"""
        # Prepare
        prepared = self.prepare()
        self.update_status(20, "Executing")
        
        # Execute
        result = self.run_workflow(prepared.cwl, prepared.params)
        
        # Finalize
        self.finalize(None, result, None, None)
        
        return zoo.SERVICE_SUCCEEDED
    
    def wrap(self):
        """Wrap workflow"""
        return self.cwl
    
    def get_processing_parameters(self):
        """Get parameters"""
        return {"max_cores": 8}

# Use in service
def my_service(conf, inputs, outputs):
    runner = MyRunner(cwl, inputs, conf, outputs, handler)
    return runner.execute()
```

## See Also

- [BaseRunner Guide](../user-guide/base-runner.md)
- [Implementing Runners](../development/implementing-runners.md)
- [ZooConf API](zoo-conf.md)
