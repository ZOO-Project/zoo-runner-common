# How to Implement a New CWL Runner for the ZOO-Project

This document serves as a **guide for developers** who wish to implement a new CWL Runner compatible with the [ZOO-Project-DRU](https://github.com/EOEPCA/zoo-project) ecosystem. It is meant to ensure **uniform structure**, **code reuse**, and **interoperability** across all runners (Calrissian, ArgoWF, WES, etc.).

---

##Project Architecture Overview

Each runner is responsible for:
- Receiving CWL + job configuration
- Wrapping or processing the workflow for a specific backend (K8s, WES, Argo, etc.)
- Monitoring execution and reporting output

All runners follow the same structure and **rely on shared components** provided in the [`zoo-runner-common`](https://github.com/AryanKhare1225/zoo-runner-common) repository.

runner_name
- zoo_<runner_name>runner
  - init.py ← Your Runner class goes here
  - handlers/ ← ExecutionHandler (optional)
  - other_utils.py ← Runner-specific helper logic
- assets ← CWL wrapper templates, if needed
- tests
  - test_main_runner<runner_name>.py ← Pytest file for validation
- README.md


---

## Prerequisites

- Python 3.8+
- Familiarity with CWL and the OGC API - Processes
- Basic knowledge of containerized job execution (e.g., WES, Kubernetes, Argo)

---

## Step-by-Step Guide

### Step 1: **Create Your Runner Class**

Create a file inside your runner directory:  
Example: `zoo_<runner_name>_runner/__init__.py`

```python
from zoo_runner_common.zoo_conf import ZooConf, ZooInputs, ZooOutputs, CWLWorkflow
from base_runner import BaseRunner  # optional
from zoostub import ZooStub
import logging


class ZooMyRunner:
    def __init__(self, cwl, conf, inputs, outputs, execution_handler=None):
        self.zoo_conf = ZooConf(conf)
        self.inputs = ZooInputs(inputs)
        self.outputs = ZooOutputs(outputs)
        self.cwl = CWLWorkflow(cwl, self.zoo_conf.workflow_id)
        self.handler = execution_handler
        self.logger = logging.getLogger(__name__)

    def execute(self):
        self.logger.info("execution started")
        ...
        return 3  # SERVICE_SUCCEEDED / SERVICE_FAILED
```
Reuse ZooConf, ZooInputs, and ZooOutputs from zoo-runner-common instead of duplicating logic.

### Step 2: Add Wrapper Assets (Optional)
If your runner needs CWL wrappers (e.g., Calrissian's stagein.yaml, maincwl.yaml, etc.), create an assets/ folder and load them using environment variables:

```bash
WRAPPER_MAIN=assets/maincwl.yaml
WRAPPER_RULES=assets/rules.yaml
```
### Step 3: Register the Runner in main_runner.py
Inside `zoo-cwl-runners/main_runner.py`, map the new runner name:

```python
RUNNERS = {
    "calrissian": ZooCalrissianRunner,
    "wes": ZooWESRunner,
    "argowf": ZooArgoWfRunner,
    "myrunner": ZooMyRunner,  # Add your runner here
}
```

### Step 4: Add a Pytest for Your Runner
Create a file in tests/ like test_main_runner_myrunner.py:

```python
def test_my_runner_invocation(tmp_path):
    ...
    result = subprocess.run([...])
    assert "Initialized myrunner" in result.stdout
```
Make sure you print something like Initialized myrunner in your class to make this test meaningful.

### Step 5: Document and Test
- Add a README.md in your runner repo.
- Add a sample config.json, inputs.json, outputs.json for local testing.
- Run test:

```bash
pytest tests/test_main_runner_myrunner.py -s
```
---
## Tips for Implementing a Runner
- Follow existing examples: zoo-calrissian-runner, zoo-argowf-runner
- Respect the function naming:

  - get_processing_parameters()

  - get_workflow_inputs()

  - assert_parameters()

- Always support environment overrides (e.g., volume size, secrets)

---

### Example Runners Implemented

| Runner	| Backend |	Features |
| ---- | ---- | ---- |
|Calrissian	|Kubernetes	|Stage-in/out, PVC, namespace mgmt|
|ArgoWF	|Argo Workflows|	YAML template builder|
|WES|	REST APIs	|OGC-compliant workflow exec|
|YourRunner|	TBD|	Your custom backend|

---

### Final Notes
- Keep your runner minimal and reusable.

- Use zoo-runner-common extensively for all shared logic.

- Follow modularity and testability.

- Add CI/CD integration using GitHub Actions if required.
