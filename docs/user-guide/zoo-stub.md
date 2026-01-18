# ZooStub User Guide

The `ZooStub` class provides a mock implementation of ZOO-Project's runtime functions for local testing and development.

## Overview

When developing ZOO services locally, you don't have access to the actual ZOO-Project runtime functions like status updates and logging. `ZooStub` provides compatible implementations that allow you to test your services outside of the ZOO environment.

## Features

- **Status Constants**: Service execution status codes
- **Status Updates**: Mock `update_status()` for testing
- **Logging**: Integration with `loguru` for local logging
- **Translation**: Mock `_()` for internationalization

## Status Constants

```python
from zoostub import ZooStub

zoo = ZooStub()

# Available status codes
zoo.SERVICE_ACCEPTED     # 0 - Service request accepted
zoo.SERVICE_STARTED      # 1 - Service execution started
zoo.SERVICE_PAUSED       # 2 - Service paused (deprecated)
zoo.SERVICE_SUCCEEDED    # 3 - Service completed successfully
zoo.SERVICE_FAILED       # 4 - Service failed
zoo.SERVICE_DEPLOYED     # 6 - Service deployed
zoo.SERVICE_UNDEPLOYED   # 7 - Service undeployed
```

## Basic Usage

### Local Testing Setup

```python
from zoostub import ZooStub

# Create stub instance
zoo = ZooStub()

def my_service(conf, inputs, outputs):
    """ZOO Service for local testing"""
    
    # Update status
    zoo.update_status(conf, 20)
    
    # Log progress
    zoo.info("Processing started")
    
    # ... processing ...
    
    zoo.info("Processing completed")
    zoo.update_status(conf, 100)
    
    return zoo.SERVICE_SUCCEEDED
```

### Status Updates

```python
from zoostub import ZooStub

zoo = ZooStub()

# Simulate progress updates
zoo.update_status(conf, 10)   # 10% complete
zoo.update_status(conf, 50)   # 50% complete
zoo.update_status(conf, 100)  # 100% complete

# Output:
# Status 10
# Status 50
# Status 100
```

In production, this calls the actual ZOO-Project C function to update the execution status.

## Logging Functions

`ZooStub` integrates with `loguru` for comprehensive logging:

### Available Log Levels

```python
from zoostub import ZooStub

zoo = ZooStub()

# Trace level (most verbose)
zoo.trace("Detailed execution trace")

# Debug level
zoo.debug("Debug information")

# Info level
zoo.info("General information")

# Success level
zoo.success("Operation completed successfully")

# Warning level
zoo.warning("Potential issue detected")

# Error level
zoo.error("An error occurred")

# Critical level (most severe)
zoo.critical("Critical system error")
```

### Example with Real Service

```python
from zoostub import ZooStub
from base_runner import BaseRunner

zoo = ZooStub()

def process_data(conf, inputs, outputs):
    """Process data with comprehensive logging"""
    
    zoo.info("Service started")
    zoo.update_status(conf, 10)
    
    try:
        # Validate inputs
        zoo.debug(f"Inputs: {inputs}")
        
        if "data_url" not in inputs:
            zoo.error("Missing required input: data_url")
            return zoo.SERVICE_FAILED
        
        zoo.info("Creating runner")
        zoo.update_status(conf, 20)
        
        runner = BaseRunner(
            cwl_path="/path/to/workflow.cwl",
            input_params=inputs,
            conf=conf
        )
        
        zoo.info("Executing workflow")
        zoo.update_status(conf, 50)
        
        result = runner.execute()
        
        zoo.success("Workflow completed successfully")
        zoo.update_status(conf, 90)
        
        # Set outputs
        outputs["result"]["value"] = result["stac_catalog"]
        
        zoo.info("Service completed")
        zoo.update_status(conf, 100)
        
        return zoo.SERVICE_SUCCEEDED
        
    except FileNotFoundError as e:
        zoo.error(f"File not found: {e}")
        return zoo.SERVICE_FAILED
        
    except Exception as e:
        zoo.critical(f"Unexpected error: {e}")
        return zoo.SERVICE_FAILED
```

## Translation Function

The `_()` function provides a mock for internationalization:

```python
from zoostub import ZooStub

zoo = ZooStub()

# Mock translation (just prints in stub)
message = zoo._("Processing started")
# Output: invoked _ with Processing started

# In production, this would use ZOO's translation system
```

## Using in Development vs Production

### Development (with ZooStub)

```python
from zoostub import ZooStub

zoo = ZooStub()

def my_service(conf, inputs, outputs):
    zoo.info("Running locally")
    zoo.update_status(conf, 50)
    # ... processing ...
    return zoo.SERVICE_SUCCEEDED

# Test locally
if __name__ == "__main__":
    conf = {"lenv": {"message": ""}}
    inputs = {"data": {"value": "test.tif"}}
    outputs = {}
    
    status = my_service(conf, inputs, outputs)
    print(f"Service returned: {status}")
```

### Production (with real ZOO)

```python
try:
    import zoo
except ImportError:
    from zoostub import ZooStub
    zoo = ZooStub()

def my_service(conf, inputs, outputs):
    """Works in both development and production"""
    zoo.info("Service started")
    zoo.update_status(conf, 50)
    # ... processing ...
    return zoo.SERVICE_SUCCEEDED
```

## Integration with BaseRunner

`ZooStub` works seamlessly with `BaseRunner`:

```python
from zoostub import ZooStub
from base_runner import BaseRunner

zoo = ZooStub()

def test_runner_locally():
    """Test a CWL workflow locally"""
    
    conf = {
        "lenv": {
            "Identifier": "test-workflow",
            "message": ""
        },
        "main": {
            "tmpPath": "/tmp/zoo-test"
        }
    }
    
    inputs = {
        "input_file": {
            "cache_file": "/path/to/test.tif",
            "mimeType": "image/tiff"
        },
        "threshold": {
            "dataType": "float",
            "value": "0.5"
        }
    }
    
    outputs = {"stac": {}}
    
    zoo.info("Starting local test")
    
    runner = BaseRunner(
        cwl_path="/path/to/app-package.cwl",
        input_params=inputs,
        conf=conf
    )
    
    zoo.info("Executing workflow")
    result = runner.execute()
    
    zoo.success(f"Result: {result}")
    
    return zoo.SERVICE_SUCCEEDED

if __name__ == "__main__":
    status = test_runner_locally()
    print(f"Test completed with status: {status}")
```

## Logging Configuration

Customize `loguru` logging when using `ZooStub`:

```python
from loguru import logger
from zoostub import ZooStub

# Configure loguru
logger.remove()  # Remove default handler
logger.add(
    "service.log",
    rotation="10 MB",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
)

zoo = ZooStub()

# Now all zoo.info(), zoo.debug(), etc. use custom config
zoo.info("Service started")
zoo.debug("Debug message")
```

## Best Practices

### 1. Import Pattern for Development/Production

```python
# ✅ DO: Support both environments
try:
    import zoo
except ImportError:
    from zoostub import ZooStub
    zoo = ZooStub()
```

### 2. Consistent Status Updates

```python
# ✅ DO: Regular status updates
zoo.update_status(conf, 0)    # Started
zoo.update_status(conf, 25)   # 1/4 complete
zoo.update_status(conf, 50)   # 1/2 complete
zoo.update_status(conf, 75)   # 3/4 complete
zoo.update_status(conf, 100)  # Complete
```

### 3. Appropriate Log Levels

```python
# ✅ DO: Use appropriate log levels
zoo.debug("Variable value: {value}")     # Development info
zoo.info("Processing step completed")    # Normal operation
zoo.warning("Using default value")       # Potential issue
zoo.error("Failed to connect to API")    # Error occurred
zoo.critical("System out of memory")     # Critical failure

# ❌ DON'T: Use info for everything
```

### 4. Error Handling with Logging

```python
# ✅ DO: Log errors with context
try:
    result = process_data()
except ValueError as e:
    zoo.error(f"Invalid data format: {e}")
    return zoo.SERVICE_FAILED
except Exception as e:
    zoo.critical(f"Unexpected error: {e}")
    return zoo.SERVICE_FAILED
```

## Testing Example

Create a complete test with `ZooStub`:

```python
from zoostub import ZooStub
from zoo_conf import ZooInputs, ZooOutputs

zoo = ZooStub()

def test_service_locally():
    """Complete local service test"""
    
    # Setup test data
    conf = {
        "lenv": {"Identifier": "test", "message": ""},
        "main": {"tmpPath": "/tmp/test"}
    }
    
    inputs = {
        "threshold": {
            "dataType": "float",
            "value": "0.75"
        },
        "input_file": {
            "cache_file": "/tmp/test.tif",
            "mimeType": "image/tiff"
        }
    }
    
    outputs = {"result": {}}
    
    # Run service
    zoo.info("=== Starting Service Test ===")
    zoo.update_status(conf, 0)
    
    # Parse inputs
    zoo_inputs = ZooInputs(inputs)
    params = zoo_inputs.get_processing_parameters()
    zoo.debug(f"Parameters: {params}")
    
    # Simulate processing
    zoo.info("Processing data...")
    zoo.update_status(conf, 50)
    
    # Set results
    zoo_outputs = ZooOutputs(outputs)
    zoo_outputs.set_output("/tmp/result.json")
    
    zoo.success("Service completed successfully")
    zoo.update_status(conf, 100)
    
    return zoo.SERVICE_SUCCEEDED

if __name__ == "__main__":
    status = test_service_locally()
    
    if status == 3:
        print("✓ Test PASSED")
    else:
        print("✗ Test FAILED")
```

## Limitations

`ZooStub` is for local testing only. It provides:

- ✅ Status code constants
- ✅ Mock status updates (prints to console)
- ✅ Logging via loguru
- ✅ Mock translation function

It does NOT provide:

- ❌ Actual ZOO-Project runtime integration
- ❌ Real status updates to ZOO server
- ❌ ZOO-Project's full API
- ❌ Multi-language translation

## See Also

- [BaseRunner User Guide](base-runner.md)
- [ZooConf User Guide](zoo-conf.md)
- [Implementing Custom Runners](../development/implementing-runners.md)
