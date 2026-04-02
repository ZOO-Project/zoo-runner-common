# Quick Start

This guide will help you get started with zoo-runner-common by implementing a simple CWL runner.

## Basic Runner Implementation

```python
try:
    import zoo
except ImportError:
    from zoo_runner_common.zoostub import ZooStub

    zoo = ZooStub()

from zoo_runner_common import BaseRunner

class MyRunner(BaseRunner):
    """Simple CWL runner implementation"""

    def wrap(self):
        return self.cwl

    def execute(self):
        """Execute the CWL workflow"""
        prepared = self.prepare()
        result = self.run_workflow(prepared.cwl, prepared.params)

        if result.success:
            self.finalize(None, {"result": result.value}, None, [])
            return self.SERVICE_SUCCEEDED
        return self.SERVICE_FAILED

    def run_workflow(self, cwl_doc, params):
        """Implement your workflow execution logic"""
        pass
```

## Using ZooConf

```python
from zoo_runner_common import ZooConf

# Parse ZOO configuration
zoo_conf = ZooConf(conf)
workflow_id = zoo_conf.workflow_id
```

## Using ZooStub for Testing

```python
from zoo_runner_common import ZooStub

zoo = ZooStub()

# Use ZOO status codes
zoo.SERVICE_SUCCEEDED  # 3
zoo.SERVICE_FAILED     # 4
```

## Complete Example

```python
from zoo_runner_common import BaseRunner
import subprocess

class SimpleRunner(BaseRunner):
    def wrap(self):
        return self.cwl

    def execute(self):
        try:
            prepared = self.prepare()
            
            # Run using cwltool
            cmd = ["cwltool", prepared.cwl]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.finalize(result.stdout, {"stdout": result.stdout}, None, [])
                return self.SERVICE_SUCCEEDED
            return self.SERVICE_FAILED
                
        except Exception as e:
            self.conf.conf["lenv"]["message"] = str(e)
            return self.SERVICE_FAILED
```

## Next Steps

- Learn about [BaseRunner API](../api/base-runner.md)
- Read the [Runner Implementation Guide](../development/implementing-runners.md)
- Explore specific runner implementations (Calrissian, Argo, WES)
