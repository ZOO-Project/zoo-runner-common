# ZooConf User Guide

The `zoo_conf` module provides essential utilities for working with ZOO-Project configuration and CWL workflows. This guide covers practical usage patterns.

## Overview

The module contains four main classes:

- **ZooConf**: Configuration handler
- **ZooInputs**: Input parameter parser with type conversion
- **ZooOutputs**: Output handler
- **CWLWorkflow**: CWL workflow parser and analyzer

## Working with ZooConf

`ZooConf` is a simple wrapper around the ZOO-Project configuration dictionary.

### Basic Usage

```python
from zoo_conf import ZooConf

def my_service(conf, inputs, outputs):
    zoo_conf = ZooConf(conf)
    
    # Get the workflow identifier
    workflow_id = zoo_conf.workflow_id  # From conf["lenv"]["Identifier"]
    
    # Access underlying conf dict
    tmp_path = zoo_conf.conf["main"]["tmpPath"]
    
    return 3
```

## Handling Inputs with ZooInputs

`ZooInputs` handles the complexity of ZOO input parsing, including type conversion and array handling.

### Type Conversion

ZOO-Project passes all values as strings. `ZooInputs` automatically converts them to appropriate Python types:

```python
from zoo_conf import ZooInputs

inputs = {
    "threshold": {
        "dataType": "float",
        "value": "0.85"
    },
    "max_iterations": {
        "dataType": "integer",
        "value": "100"
    },
    "enable_cache": {
        "dataType": "boolean",
        "value": "1"
    }
}

zoo_inputs = ZooInputs(inputs)
params = zoo_inputs.get_processing_parameters()

# Result:
# {
#     'threshold': 0.85,         # float
#     'max_iterations': 100,     # int
#     'enable_cache': 1          # int (boolean)
# }
```

### File Inputs

File inputs are converted to CWL File objects:

```python
inputs = {
    "input_raster": {
        "cache_file": "/tmp/zTMPykgmh8/data.tif",
        "mimeType": "image/tiff"
    },
    "config_file": {
        "cache_file": "/tmp/zTMPykgmh8/config.json",
        "mimeType": "application/json"
    }
}

zoo_inputs = ZooInputs(inputs)
params = zoo_inputs.get_processing_parameters()

# Result:
# {
#     'input_raster': {
#         'class': 'File',
#         'path': '/tmp/zTMPykgmh8/data.tif',
#         'format': 'image/tiff'
#     },
#     'config_file': {
#         'class': 'File',
#         'path': '/tmp/zTMPykgmh8/config.json',
#         'format': 'application/json'
#     }
# }
```

### Array Inputs

ZOO-Project has a quirk: arrays with one element are converted to strings. `ZooInputs` automatically handles this:

```python
inputs = {
    "bands": {
        "maxOccurs": "3",
        "value": "B02"  # Single value, but should be array
    }
}

zoo_inputs = ZooInputs(inputs)

# Automatically converted to array:
# inputs["bands"]["value"] = ["B02"]
```

### Getting Individual Input Values

```python
zoo_inputs = ZooInputs(inputs)

# Get specific input
try:
    threshold = zoo_inputs.get_input_value("threshold")
except KeyError:
    print("threshold parameter not provided")
```

## Handling Outputs with ZooOutputs

`ZooOutputs` simplifies setting service output values.

### Basic Output

```python
from zoo_conf import ZooOutputs

def my_service(conf, inputs, outputs):
    # ... processing ...
    
    zoo_outputs = ZooOutputs(outputs)
    
    # Set the result
    zoo_outputs.set_output("/tmp/results/catalog.json")
    
    return 3
```

### Multiple Outputs

```python
outputs = {
    "result": {},
    "metadata": {}
}

zoo_outputs = ZooOutputs(outputs)

# Sets the primary output (first key)
zoo_outputs.set_output("/tmp/result.tif")

# For additional outputs, set directly
outputs["metadata"]["value"] = "/tmp/metadata.json"
```

### Getting Output Parameters

```python
zoo_outputs = ZooOutputs(outputs)
output_params = zoo_outputs.get_output_parameters()
# {'result': '/tmp/result.tif', 'metadata': '/tmp/metadata.json'}
```

## Working with CWL Workflows

`CWLWorkflow` provides utilities for parsing and analyzing CWL workflows.

### Loading a Workflow

```python
from zoo_conf import CWLWorkflow

# Load from dict
cwl_dict = {
    "cwlVersion": "v1.0",
    "$graph": [
        {
            "class": "Workflow",
            "id": "main-workflow",
            "label": "My Workflow",
            "doc": "Process satellite imagery",
            "inputs": [...],
            "outputs": [...],
            "steps": [...]
        }
    ],
    "s:softwareVersion": "1.2.0"
}

workflow = CWLWorkflow(cwl_dict, "main-workflow")
```

### Getting Workflow Metadata

```python
# Version
version = workflow.get_version()  # "1.2.0"

# Label
label = workflow.get_label()  # "My Workflow"

# Documentation
doc = workflow.get_doc()  # "Process satellite imagery"
```

### Analyzing Workflow Inputs

```python
# Get all inputs
all_inputs = workflow.get_workflow_inputs()
# ['input_data', 'threshold', 'bands', 'output_format']

# Get only mandatory inputs (no default values)
required_inputs = workflow.get_workflow_inputs(mandatory=True)
# ['input_data']

# Validate that required inputs are provided
zoo_inputs = ZooInputs(inputs)
for required in required_inputs:
    try:
        zoo_inputs.get_input_value(required)
    except KeyError:
        raise ValueError(f"Missing required input: {required}")
```

### Resource Requirements

Analyze and aggregate resource requirements across the workflow:

```python
resources = workflow.eval_resource()

# Result:
# {
#     'coresMin': [2, 4, 1],      # Requirements from each step
#     'coresMax': [4, 8, 2],
#     'ramMin': [2048, 4096, 512],
#     'ramMax': [4096, 8192, 1024],
#     'tmpdirMin': [1024],
#     'tmpdirMax': [2048],
#     'outdirMin': [512],
#     'outdirMax': [1024]
# }

# Calculate totals
total_cores_min = sum(resources['coresMin'])  # 7
total_ram_min = sum(resources['ramMin'])      # 6656 MB

# Use maximum values for resource allocation
max_cores = max(resources['coresMax'])  # 8
max_ram = max(resources['ramMax'])      # 8192 MB

print(f"Request {max_cores} cores and {max_ram} MB RAM")
```

### Scatter Operations

The resource evaluator automatically accounts for scatter operations:

```python
import os

# Set scatter multiplier (default: 2)
os.environ["SCATTER_MULTIPLIER"] = "3"

workflow = CWLWorkflow(cwl_dict, "main-workflow")
resources = workflow.eval_resource()

# Steps with scatter will have their resources multiplied by 3
```

## Complete Service Example

Here's a complete ZOO service using all the utilities:

```python
from zoo_conf import ZooConf, ZooInputs, ZooOutputs, CWLWorkflow
from base_runner import BaseRunner

def process_imagery(conf, inputs, outputs):
    """
    ZOO Service for processing satellite imagery
    """
    try:
        # Parse configuration
        zoo_conf = ZooConf(conf)
        workflow_id = zoo_conf.workflow_id
        
        # Load CWL workflow
        cwl_path = f"/opt/zooservices/{workflow_id}/app-package.cwl"
        with open(cwl_path) as f:
            import yaml
            cwl_dict = yaml.safe_load(f)
        
        workflow = CWLWorkflow(cwl_dict, workflow_id)
        
        # Validate inputs
        required_inputs = workflow.get_workflow_inputs(mandatory=True)
        zoo_inputs = ZooInputs(inputs)
        
        for required in required_inputs:
            try:
                zoo_inputs.get_input_value(required)
            except KeyError:
                conf["lenv"]["message"] = f"Missing required input: {required}"
                return 4  # SERVICE_FAILED
        
        # Get processing parameters
        params = zoo_inputs.get_processing_parameters()
        
        # Evaluate resources
        resources = workflow.eval_resource()
        total_ram = sum(resources['ramMin'])
        conf["lenv"]["message"] = f"Workflow requires {total_ram} MB RAM"
        
        # Create runner
        runner = BaseRunner(
            cwl_path=cwl_path,
            input_params=params,
            conf=conf
        )
        
        # Execute
        result = runner.execute()
        
        # Set outputs
        zoo_outputs = ZooOutputs(outputs)
        zoo_outputs.set_output(result["stac_catalog"])
        
        return 3  # SERVICE_SUCCEEDED
        
    except Exception as e:
        conf["lenv"]["message"] = str(e)
        return 4  # SERVICE_FAILED
```

## Best Practices

### 1. Always Use ZooInputs for Type Conversion

```python
# ✅ DO: Use ZooInputs for automatic type conversion
zoo_inputs = ZooInputs(inputs)
params = zoo_inputs.get_processing_parameters()

# ❌ DON'T: Manual parsing (error-prone)
threshold = float(inputs["threshold"]["value"])
```

### 2. Validate Mandatory Inputs

```python
# ✅ DO: Check for required inputs
workflow = CWLWorkflow(cwl_dict, workflow_id)
required = workflow.get_workflow_inputs(mandatory=True)

zoo_inputs = ZooInputs(inputs)
for inp in required:
    try:
        zoo_inputs.get_input_value(inp)
    except KeyError:
        return 4  # SERVICE_FAILED
```

### 3. Use Resource Evaluation

```python
# ✅ DO: Evaluate and communicate resource requirements
resources = workflow.eval_resource()
total_ram = sum(resources['ramMin'])
conf["lenv"]["message"] = f"Requires {total_ram} MB RAM"
```

### 4. Handle Arrays Correctly

```python
# ✅ DO: Let ZooInputs handle array conversion
zoo_inputs = ZooInputs(inputs)  # Handles single-value arrays automatically

# ❌ DON'T: Assume inputs["array"]["value"] is always a list
```

## Troubleshooting

### Array Input Not Recognized

**Problem**: Single-value array becomes a string

**Solution**: Use `ZooInputs` - it automatically handles this:

```python
zoo_inputs = ZooInputs(inputs)
# Arrays with maxOccurs > 1 are automatically converted
```

### Type Conversion Errors

**Problem**: String values not converting to numbers

**Solution**: Ensure `dataType` is set in input definition:

```python
inputs = {
    "threshold": {
        "dataType": "float",  # Required for conversion
        "value": "0.85"
    }
}
```

### Resource Evaluation Returns Empty Lists

**Problem**: `eval_resource()` returns empty lists

**Solution**: Ensure CWL workflow has ResourceRequirement in requirements or hints:

```yaml
requirements:
  ResourceRequirement:
    coresMin: 2
    ramMin: 2048
```

## See Also

- [API Reference: ZooConf](../api/zoo-conf.md)
- [BaseRunner User Guide](base-runner.md)
- [Implementing Custom Runners](../development/implementing-runners.md)
