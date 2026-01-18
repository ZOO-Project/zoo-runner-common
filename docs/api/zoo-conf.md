# ZooConf API Reference

The `zoo_conf` module provides utilities for working with CWL workflows and ZOO-Project configuration.

## Classes

### ZooConf

Main configuration handler for ZOO-Project services.

::: zoo_conf.ZooConf
    options:
      show_source: true
      heading_level: 4

### ZooInputs

Handler for ZOO-Project service inputs with type conversion and validation.

::: zoo_conf.ZooInputs
    options:
      show_source: true
      heading_level: 4

#### Methods

##### get_input_value(key)

Get the value of a specific input parameter.

**Parameters:**

- `key` (str): The input parameter key

**Returns:**

- The input value

**Raises:**

- `KeyError`: If the input key doesn't exist

**Example:**

```python
zoo_inputs = ZooInputs(inputs)
url = zoo_inputs.get_input_value("data_url")
```

##### get_processing_parameters()

Returns a dictionary of all input parameters with proper type conversion.

Handles:

- Numeric types (int, float, double)
- Booleans
- Files with MIME types
- Arrays

**Returns:**

- `dict`: Dictionary of input parameters ready for CWL execution

**Example:**

```python
zoo_inputs = ZooInputs(inputs)
params = zoo_inputs.get_processing_parameters()
# {'threshold': 0.5, 'input_file': {'class': 'File', 'path': '/tmp/data.tif', 'format': 'image/tiff'}}
```

### ZooOutputs

Handler for ZOO-Project service outputs.

::: zoo_conf.ZooOutputs
    options:
      show_source: true
      heading_level: 4

#### Methods

##### get_output_parameters()

Returns a dictionary of all output parameters.

**Returns:**

- `dict`: Dictionary mapping output keys to their values

**Example:**

```python
zoo_outputs = ZooOutputs(outputs)
output_params = zoo_outputs.get_output_parameters()
```

##### set_output(value)

Set the output result value for the primary output.

**Parameters:**

- `value`: The output value to set

**Example:**

```python
zoo_outputs = ZooOutputs(outputs)
zoo_outputs.set_output("/tmp/results/catalog.json")
```

## CWL Workflow Classes

### CWLWorkflow

Parser and utility class for CWL workflows.

::: zoo_conf.CWLWorkflow
    options:
      show_source: true
      heading_level: 4

#### Methods

##### get_version()

Get the workflow version from CWL metadata.

**Returns:**

- `str`: Software version from `s:softwareVersion` field

##### get_label()

Get the workflow label.

**Returns:**

- `str`: Workflow label

##### get_doc()

Get the workflow documentation.

**Returns:**

- `str`: Workflow documentation string

##### get_workflow()

Get the parsed CWL workflow object.

**Returns:**

- `cwl_utils.parser.cwl_v1_0.Workflow`: The parsed workflow object

##### get_workflow_inputs(mandatory=False)

Get list of workflow input parameter names.

**Parameters:**

- `mandatory` (bool): If True, only return mandatory inputs (no defaults)

**Returns:**

- `list`: List of input parameter names

**Example:**

```python
cwl_workflow = CWLWorkflow(cwl_dict, "main-workflow")
all_inputs = cwl_workflow.get_workflow_inputs()
# ['input_data', 'threshold', 'output_format']

required_inputs = cwl_workflow.get_workflow_inputs(mandatory=True)
# ['input_data']
```

##### eval_resource()

Evaluate and aggregate resource requirements from the workflow and all steps.

Considers:

- Workflow-level resource requirements
- Step-level resource requirements
- Scatter operations (multiplied by `SCATTER_MULTIPLIER` env var, default: 2)

**Returns:**

- `dict`: Dictionary with aggregated resource requirements:
    - `coresMin`, `coresMax`: CPU cores
    - `ramMin`, `ramMax`: RAM in MB
    - `tmpdirMin`, `tmpdirMax`: Temporary directory space in MB
    - `outdirMin`, `outdirMax`: Output directory space in MB

**Example:**

```python
cwl_workflow = CWLWorkflow(cwl_dict, "main-workflow")
resources = cwl_workflow.eval_resource()
# {
#     'coresMin': [2, 4],
#     'ramMin': [2048, 4096],
#     ...
# }
```

##### get_resource_requirement(elem)

Static method to extract ResourceRequirement from a CWL element.

**Parameters:**

- `elem`: CWL CommandLineTool or Workflow object

**Returns:**

- ResourceRequirement object or None

### ResourceRequirement

Data class for CWL resource requirements (used for hints).

::: zoo_conf.ResourceRequirement
    options:
      show_source: true
      heading_level: 4

**Attributes:**

- `coresMin` (int): Minimum CPU cores
- `coresMax` (int): Maximum CPU cores
- `ramMin` (int): Minimum RAM in MB
- `ramMax` (int): Maximum RAM in MB
- `tmpdirMin` (int): Minimum temporary directory space in MB
- `tmpdirMax` (int): Maximum temporary directory space in MB
- `outdirMin` (int): Minimum output directory space in MB
- `outdirMax` (int): Maximum output directory space in MB

## Usage Examples

### Basic Configuration Handling

```python
from zoo_conf import ZooConf, ZooInputs, ZooOutputs

def my_service(conf, inputs, outputs):
    """ZOO Service function"""
    # Parse configuration
    zoo_conf = ZooConf(conf)
    workflow_id = zoo_conf.workflow_id
    
    # Handle inputs
    zoo_inputs = ZooInputs(inputs)
    params = zoo_inputs.get_processing_parameters()
    
    # Handle outputs
    zoo_outputs = ZooOutputs(outputs)
    zoo_outputs.set_output("/path/to/result")
    
    return 3  # SERVICE_SUCCEEDED
```

### CWL Workflow Analysis

```python
from zoo_conf import CWLWorkflow

# Load CWL workflow
cwl_dict = {
    "cwlVersion": "v1.0",
    "$graph": [...],
    "s:softwareVersion": "1.0.0"
}

workflow = CWLWorkflow(cwl_dict, "main-workflow")

# Get metadata
print(f"Version: {workflow.get_version()}")
print(f"Label: {workflow.get_label()}")

# Get inputs
mandatory_inputs = workflow.get_workflow_inputs(mandatory=True)
print(f"Required inputs: {mandatory_inputs}")

# Evaluate resources
resources = workflow.eval_resource()
total_cores = sum(resources['coresMin'])
total_ram = sum(resources['ramMin'])
print(f"Requires {total_cores} cores and {total_ram} MB RAM")
```

### Type Conversion Example

```python
# ZOO inputs with various types
inputs = {
    "threshold": {
        "dataType": "float",
        "value": "0.75"
    },
    "iterations": {
        "dataType": "integer",
        "value": "10"
    },
    "input_file": {
        "cache_file": "/tmp/data.tif",
        "mimeType": "image/tiff"
    },
    "bands": {
        "dataType": "string",
        "maxOccurs": "3",
        "value": ["B02", "B03", "B04"]
    }
}

zoo_inputs = ZooInputs(inputs)
params = zoo_inputs.get_processing_parameters()

# Automatic type conversion:
# {
#     'threshold': 0.75,           # float
#     'iterations': 10,             # int
#     'input_file': {               # File object
#         'class': 'File',
#         'path': '/tmp/data.tif',
#         'format': 'image/tiff'
#     },
#     'bands': ['B02', 'B03', 'B04']  # array
# }
```

## See Also

- [User Guide: ZooConf](../user-guide/zoo-conf.md)
- [BaseRunner API](base-runner.md)
- [Implementing Custom Runners](../development/implementing-runners.md)
