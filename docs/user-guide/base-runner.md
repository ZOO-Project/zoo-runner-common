# BaseRunner Guide

## Overview

`BaseRunner` is the abstract base class for all CWL workflow runners in the ZOO-Project ecosystem.

## Class Structure

```python
from base_runner import BaseRunner

class MyRunner(BaseRunner):
    """Custom CWL runner implementation"""
    
    def __init__(self, cwl, inputs, conf, outputs, execution_handler=None):
        super().__init__(cwl, inputs, conf, outputs, execution_handler)
    
    def execute(self):
        """Implement workflow execution logic"""
        # Your implementation
        pass
```

## Constructor Parameters

```python
def __init__(self, cwl, inputs, conf, outputs, execution_handler=None)
```

**Parameters:**

- `cwl`: CWL workflow document (path or content)
- `inputs`: ZOO inputs dictionary
- `conf`: ZOO configuration dictionary
- `outputs`: ZOO outputs dictionary
- `execution_handler`: Optional execution handler (e.g., CommonExecutionHandler)

## Core Methods

### prepare()

Shared pre-execution logic that:
- Calls `execution_handler.pre_execution_hook()`
- Prepares processing parameters
- Sets up environment

```python
def prepare(self):
    """Prepare for execution"""
    logger.info("execution started")
    self.execution_handler.pre_execution_hook()
    # Additional preparation...
```

**Usage:**

```python
runner = MyRunner(cwl, inputs, conf, outputs, handler)
runner.prepare()
```

### execute()

Abstract method that must be implemented by subclasses.

```python
@abstractmethod
def execute(self):
    """Execute the workflow"""
    pass
```

**Implementation:**

```python
class MyRunner(BaseRunner):
    def execute(self):
        """Execute workflow"""
        try:
            self.prepare()
            result = self.run_workflow()
            self.log_output(result)
            return zoo.SERVICE_SUCCEEDED
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return zoo.SERVICE_FAILED
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
runner.update_status(10, "Downloading inputs...")
runner.update_status(50, "Processing data...")
runner.update_status(90, "Uploading results...")
runner.update_status(100, "Complete")
```

### validate_inputs()

Validate input parameters before execution.

```python
def validate_inputs(self) -> bool
```

**Returns:**
- bool: True if inputs are valid

**Override:**

```python
class MyRunner(BaseRunner):
    def validate_inputs(self):
        """Custom validation"""
        if "required_param" not in self.inputs:
            logger.error("Missing required parameter")
            return False
        return True
```

### log_output()

Log output information.

```python
def log_output(self, output)
```

**Example:**

```python
result = {"status": "success", "files": ["output.tif"]}
runner.log_output(result)
```

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
# Returns: "my-process-12345"
```

## Execution Handler Integration

BaseRunner integrates with execution handlers for lifecycle hooks:

```python
from base_runner import BaseRunner
from zoo_template_common import CommonExecutionHandler

class MyHandler(CommonExecutionHandler):
    def pre_execution_hook(self):
        """Setup before execution"""
        print("Setting up...")
    
    def post_execution_hook(self, log, output, usage_report, tool_logs):
        """Cleanup after execution"""
        print("Cleaning up...")

# Use with runner
handler = MyHandler(conf, outputs)
runner = MyRunner(cwl, inputs, conf, outputs, handler)

# Handler hooks are called automatically
runner.prepare()  # Calls handler.pre_execution_hook()
```

## Available Handler Methods

The execution handler provides these methods:

- `pre_execution_hook()`: Called before execution
- `post_execution_hook(log, output, usage_report, tool_logs)`: Called after execution
- `get_secrets()`: Get secrets from configuration
- `get_additional_parameters()`: Get workflow parameters
- `get_pod_env_vars()`: Get pod environment variables
- `get_pod_node_selector()`: Get node selector for scheduling
- `handle_outputs(...)`: Process outputs
- `set_job_id(job_id)`: Set job identifier

## Default Handler

If no handler is provided, BaseRunner creates a default handler:

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
```

## Attributes

### cwl
CWL workflow document.

```python
runner.cwl  # Path or content
```

### inputs
ZOO inputs dictionary.

```python
runner.inputs  # {"param1": {"value": "..."}}
```

### conf
ZOO configuration dictionary.

```python
runner.conf  # {"lenv": {...}, "main": {...}}
```

### outputs
ZOO outputs dictionary.

```python
runner.outputs  # {"result": {...}}
```

### execution_handler
Execution handler instance.

```python
runner.execution_handler  # Handler instance
```

### namespace_name
Kubernetes namespace name.

```python
runner.namespace_name  # "process-12345"
```

## Complete Example

```python
from base_runner import BaseRunner
from zoo_template_common import CommonExecutionHandler
import subprocess
import logging

logger = logging.getLogger(__name__)

class SimpleRunner(BaseRunner):
    """Simple CWL runner using cwltool"""
    
    def execute(self):
        """Execute workflow with cwltool"""
        try:
            # Prepare
            self.prepare()
            self.update_status(10, "Preparing execution")
            
            # Validate
            if not self.validate_inputs():
                return zoo.SERVICE_FAILED
            
            self.update_status(30, "Executing workflow")
            
            # Execute with cwltool
            cmd = ["cwltool", self.cwl, "--"]
            for key, value in self.inputs.items():
                cmd.append(f"{key}={value['value']}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.update_status(90, "Processing outputs")
                self.outputs["result"] = {"value": result.stdout}
                self.log_output(self.outputs)
                
                # Call post-execution hook
                self.execution_handler.post_execution_hook(
                    result.stdout, self.outputs, None, None
                )
                
                self.update_status(100, "Complete")
                return zoo.SERVICE_SUCCEEDED
            else:
                logger.error(f"Execution failed: {result.stderr}")
                return zoo.SERVICE_FAILED
                
        except Exception as e:
            logger.error(f"Error: {e}")
            return zoo.SERVICE_FAILED

# ZOO Service
def my_service(conf, inputs, outputs):
    """ZOO Service using SimpleRunner"""
    cwl = conf["lenv"]["cwl_document"]
    
    handler = CommonExecutionHandler(conf, outputs)
    runner = SimpleRunner(cwl, inputs, conf, outputs, handler)
    
    return runner.execute()
```

## Best Practices

1. **Always call prepare()**: Ensures handler hooks are executed
2. **Use update_status()**: Keep users informed of progress
3. **Validate inputs**: Check parameters before execution
4. **Handle errors**: Catch and log exceptions
5. **Log important events**: Use logger for debugging
6. **Update outputs**: Populate outputs dictionary with results

## See Also

- [ZooConf](zoo-conf.md) - Configuration parsing
- [Implementing Runners](../development/implementing-runners.md) - Create custom runners
- [API Reference](../api/base-runner.md) - Complete API documentation
