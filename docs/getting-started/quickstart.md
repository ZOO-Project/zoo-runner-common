# Quick Start

This guide will help you get started with zoo-runner-common by implementing a simple CWL runner.

## Basic Runner Implementation

```python
from base_runner import BaseRunner

class MyRunner(BaseRunner):
    """Simple CWL runner implementation"""
    
    def __init__(self, conf, inputs, outputs):
        super().__init__(conf, inputs, outputs)
        
    def execute(self):
        """Execute the CWL workflow"""
        # 1. Prepare the workflow
        cwl_document = self.get_cwl_document()
        
        # 2. Execute
        result = self.run_workflow(cwl_document)
        
        # 3. Return status
        if result.success:
            return self.SERVICE_SUCCEEDED
        else:
            return self.SERVICE_FAILED
            
    def run_workflow(self, cwl_doc):
        """Implement your workflow execution logic"""
        # Your implementation here
        pass
```

## Using ZooConf

```python
from zoo_conf import ZooConf

# Parse ZOO configuration
zoo_conf = ZooConf(conf)

# Access inputs
input_data = zoo_conf.get_input("input_name")

# Access outputs
output_spec = zoo_conf.get_output("output_name")
```

## Using ZooStub for Testing

```python
from zoostub import ZOO

# Create mock configuration
conf = {
    "lenv": {"message": ""},
    "main": {"tmpPath": "/tmp"}
}

# Use ZOO status codes
ZOO.SERVICE_SUCCEEDED  # 3
ZOO.SERVICE_FAILED     # 4
```

## Complete Example

```python
from base_runner import BaseRunner
import subprocess

class SimpleRunner(BaseRunner):
    def execute(self):
        try:
            # Get CWL document
            cwl_path = self.get_cwl_document()
            
            # Prepare inputs
            inputs_file = self.prepare_inputs()
            
            # Run using cwltool
            cmd = ["cwltool", "--outdir", self.output_dir, cwl_path, inputs_file]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Process outputs
                self.process_outputs()
                return self.SERVICE_SUCCEEDED
            else:
                self.set_error(f"Execution failed: {result.stderr}")
                return self.SERVICE_FAILED
                
        except Exception as e:
            self.set_error(str(e))
            return self.SERVICE_FAILED
```

## Next Steps

- Learn about [BaseRunner API](../api/base-runner.md)
- Read the [Runner Implementation Guide](../development/implementing-runners.md)
- Explore specific runner implementations (Calrissian, Argo, WES)
