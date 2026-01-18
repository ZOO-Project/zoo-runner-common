# Implementing a New Runner

This guide walks through implementing a new CWL runner for ZOO-Project.

## Overview

To create a new runner, you need to:

1. Extend `BaseRunner`
2. Implement the `execute()` method
3. Handle workflow execution logic
4. Process outputs

## Basic Structure

```python
from base_runner import BaseRunner
import logging

logger = logging.getLogger(__name__)

class MyRunner(BaseRunner):
    """
    Custom CWL runner implementation.
    
    This runner executes CWL workflows using [your backend].
    """
    
    def __init__(self, cwl, inputs, conf, outputs, execution_handler=None):
        """Initialize runner"""
        super().__init__(cwl, inputs, conf, outputs, execution_handler)
        # Add custom initialization
        self.client = None
    
    def execute(self):
        """Execute the workflow"""
        try:
            # 1. Prepare
            self.prepare()
            self.update_status(10, "Initializing")
            
            # 2. Validate
            if not self.validate_inputs():
                return self.SERVICE_FAILED
            
            # 3. Execute workflow
            self.update_status(30, "Executing workflow")
            result = self._run_workflow()
            
            # 4. Process outputs
            self.update_status(80, "Processing outputs")
            self._process_outputs(result)
            
            # 5. Finish
            self.update_status(100, "Complete")
            return self.SERVICE_SUCCEEDED
            
        except Exception as e:
            logger.error(f"Execution failed: {e}", exc_info=True)
            self.conf["lenv"]["message"] = str(e)
            return self.SERVICE_FAILED
    
    def _run_workflow(self):
        """Execute workflow on backend"""
        # Implement your workflow execution logic
        pass
    
    def _process_outputs(self, result):
        """Process workflow outputs"""
        # Process and populate self.outputs
        pass
```

## Step-by-Step Implementation

### Step 1: Setup Project

Create your runner package:

```bash
mkdir zoo-myrunner
cd zoo-myrunner
```

Create `setup.py`:

```python
from setuptools import setup, find_packages

setup(
    name="zoo-myrunner",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "zoo-runner-common>=0.1.0",
        # Add your specific dependencies
    ],
    author="Your Name",
    description="My CWL runner for ZOO-Project",
)
```

### Step 2: Implement Runner

Create `zoo_myrunner/runner.py`:

```python
from base_runner import BaseRunner
import logging
import subprocess
import json
import os

logger = logging.getLogger(__name__)

class MyRunner(BaseRunner):
    """My CWL runner implementation"""
    
    def __init__(self, cwl, inputs, conf, outputs, execution_handler=None):
        super().__init__(cwl, inputs, conf, outputs, execution_handler)
        self.work_dir = conf.get("main", {}).get("tmpPath", "/tmp")
        self.job_id = None
    
    def execute(self):
        """Execute CWL workflow"""
        try:
            # Prepare execution
            self.prepare()
            self.update_status(10, "Preparing workflow")
            
            # Validate inputs
            if not self.validate_inputs():
                raise ValueError("Input validation failed")
            
            # Setup execution environment
            self.update_status(20, "Setting up environment")
            self._setup_environment()
            
            # Submit workflow
            self.update_status(30, "Submitting workflow")
            self.job_id = self._submit_workflow()
            
            # Notify handler of job ID
            self.execution_handler.set_job_id(self.job_id)
            
            # Monitor execution
            self.update_status(40, "Executing workflow")
            result = self._monitor_execution()
            
            # Download outputs
            self.update_status(80, "Downloading outputs")
            self._download_outputs(result)
            
            # Post-process
            self.update_status(90, "Post-processing")
            self._post_process()
            
            # Complete
            self.update_status(100, "Workflow complete")
            return self.SERVICE_SUCCEEDED
            
        except Exception as e:
            logger.error(f"Execution failed: {e}", exc_info=True)
            self.conf["lenv"]["message"] = str(e)
            return self.SERVICE_FAILED
    
    def _setup_environment(self):
        """Setup execution environment"""
        # Get environment variables from handler
        env_vars = self.execution_handler.get_pod_env_vars()
        if env_vars:
            os.environ.update(env_vars)
        
        # Get additional parameters
        params = self.execution_handler.get_additional_parameters()
        self.max_cores = params.get("max_cores", 4)
        self.max_ram = params.get("max_ram", "8G")
        
        logger.info(f"Environment configured: cores={self.max_cores}, ram={self.max_ram}")
    
    def _submit_workflow(self):
        """Submit workflow to backend"""
        # Example: submit to a workflow engine
        cmd = [
            "my-workflow-tool", "submit",
            "--cwl", self.cwl,
            "--inputs", self._prepare_inputs_file(),
            "--cores", str(self.max_cores),
            "--memory", self.max_ram
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        job_id = result.stdout.strip()
        
        logger.info(f"Workflow submitted: {job_id}")
        return job_id
    
    def _prepare_inputs_file(self):
        """Prepare inputs file for workflow"""
        inputs_file = os.path.join(self.work_dir, "inputs.json")
        
        # Convert ZOO inputs to CWL inputs format
        cwl_inputs = {}
        for key, value in self.inputs.items():
            cwl_inputs[key] = value.get("value")
        
        with open(inputs_file, "w") as f:
            json.dump(cwl_inputs, f)
        
        return inputs_file
    
    def _monitor_execution(self):
        """Monitor workflow execution"""
        import time
        
        while True:
            status = self._get_job_status()
            
            if status["state"] == "completed":
                logger.info("Workflow completed successfully")
                return status
            elif status["state"] == "failed":
                raise RuntimeError(f"Workflow failed: {status.get('error')}")
            elif status["state"] == "running":
                progress = 40 + int(status.get("progress", 0) * 0.4)
                self.update_status(progress, f"Running: {status.get('step', 'processing')}")
            
            time.sleep(10)
    
    def _get_job_status(self):
        """Get job status from backend"""
        cmd = ["my-workflow-tool", "status", self.job_id]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    
    def _download_outputs(self, result):
        """Download workflow outputs"""
        output_dir = os.path.join(self.work_dir, "outputs")
        os.makedirs(output_dir, exist_ok=True)
        
        # Download outputs from backend
        cmd = ["my-workflow-tool", "outputs", self.job_id, "--dest", output_dir]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Populate ZOO outputs
        for output_name in self.outputs.keys():
            output_path = os.path.join(output_dir, f"{output_name}.json")
            if os.path.exists(output_path):
                with open(output_path) as f:
                    self.outputs[output_name]["value"] = f.read()
        
        logger.info("Outputs downloaded")
    
    def _post_process(self):
        """Post-process outputs"""
        # Call handler post-execution hook
        self.execution_handler.post_execution_hook(
            log=None,
            output=self.outputs,
            usage_report=None,
            tool_logs=None
        )
        
        # Additional post-processing
        self.execution_handler.handle_outputs(None, self.outputs, None, None)
```

### Step 3: Create ZOO Service

Create `zoo_myrunner/service.py`:

```python
from zoo_myrunner.runner import MyRunner
from zoo_template_common import CommonExecutionHandler

def execute_workflow(conf, inputs, outputs):
    """
    ZOO Service for executing CWL workflows with MyRunner.
    
    Args:
        conf: ZOO configuration dictionary
        inputs: ZOO inputs dictionary
        outputs: ZOO outputs dictionary
    
    Returns:
        int: ZOO service status code (3=success, 4=failure)
    """
    try:
        # Get CWL document
        cwl = conf["lenv"].get("cwl_document")
        if not cwl:
            conf["lenv"]["message"] = "No CWL document provided"
            return 4
        
        # Create execution handler
        handler = CommonExecutionHandler(conf, outputs)
        
        # Create and execute runner
        runner = MyRunner(cwl, inputs, conf, outputs, handler)
        status = runner.execute()
        
        return status
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Service failed: {e}", exc_info=True)
        conf["lenv"]["message"] = str(e)
        return 4
```

### Step 4: Add Configuration

Create `zoo_myrunner/__init__.py`:

```python
"""My CWL Runner for ZOO-Project"""

__version__ = "0.1.0"

from .runner import MyRunner
from .service import execute_workflow

__all__ = ["MyRunner", "execute_workflow"]
```

### Step 5: Write Tests

Create `tests/test_myrunner.py`:

```python
import pytest
from zoo_myrunner import MyRunner
from unittest.mock import Mock, patch

def test_runner_initialization():
    """Test runner initialization"""
    cwl = "/path/to/workflow.cwl"
    inputs = {"input1": {"value": "test"}}
    conf = {"lenv": {"message": ""}, "main": {"tmpPath": "/tmp"}}
    outputs = {}
    
    runner = MyRunner(cwl, inputs, conf, outputs)
    
    assert runner.cwl == cwl
    assert runner.inputs == inputs
    assert runner.conf == conf
    assert runner.outputs == outputs

@patch('subprocess.run')
def test_workflow_submission(mock_run):
    """Test workflow submission"""
    mock_run.return_value = Mock(stdout="job-12345", returncode=0)
    
    runner = MyRunner("/workflow.cwl", {}, {"lenv": {}, "main": {}}, {})
    runner._setup_environment()
    job_id = runner._submit_workflow()
    
    assert job_id == "job-12345"
    assert mock_run.called

def test_input_preparation():
    """Test input file preparation"""
    inputs = {
        "input1": {"value": "value1"},
        "input2": {"value": "value2"}
    }
    
    runner = MyRunner("/workflow.cwl", inputs, {"main": {"tmpPath": "/tmp"}}, {})
    inputs_file = runner._prepare_inputs_file()
    
    import json
    with open(inputs_file) as f:
        cwl_inputs = json.load(f)
    
    assert cwl_inputs["input1"] == "value1"
    assert cwl_inputs["input2"] == "value2"
```

### Step 6: Add Documentation

Create `README.md`:

```markdown
# My CWL Runner for ZOO-Project

CWL runner implementation using [your backend].

## Installation

```bash
pip install zoo-myrunner
```

## Usage

```python
from zoo_myrunner import MyRunner
from zoo_template_common import CommonExecutionHandler

handler = CommonExecutionHandler(conf, outputs)
runner = MyRunner(cwl, inputs, conf, outputs, handler)
status = runner.execute()
```

## Configuration

Set environment variables:

- `MY_BACKEND_URL`: Backend API URL
- `MY_BACKEND_TOKEN`: Authentication token

## Features

- Automatic workflow submission
- Progress monitoring
- Output retrieval
- Error handling
```

### Step 7: Package and Publish

Build the package:

```bash
python setup.py sdist bdist_wheel
```

Publish to PyPI:

```bash
pip install twine
twine upload dist/*
```

## Integration with zoo-cwl-runners

To integrate with the main runners package:

1. Add to `zoo-cwl-runners/main_runner.py`:

```python
def select_runner():
    """Select appropriate runner"""
    runner_type = os.environ.get("ZOO_RUNNER", "calrissian")
    
    if runner_type == "myrunner":
        from zoo_myrunner import MyRunner
        return MyRunner
    # ... other runners
```

2. Add to dependencies:

```python
install_requires=[
    "zoo-myrunner>=0.1.0",
]
```

## Best Practices

1. **Error Handling**: Catch and log all exceptions
2. **Status Updates**: Keep users informed of progress
3. **Cleanup**: Clean up temporary files and resources
4. **Testing**: Write comprehensive unit and integration tests
5. **Documentation**: Document configuration and usage
6. **Logging**: Use structured logging for debugging

## See Also

- [BaseRunner API](../api/base-runner.md)
- [BaseRunner User Guide](../user-guide/base-runner.md)
- [ZooConf User Guide](../user-guide/zoo-conf.md)
- [zoo-cwl-runners Documentation](https://zoo-cwl-runners.readthedocs.io) - Real implementation examples
- [ZOO-Project Documentation](https://zoo-project.org/)
