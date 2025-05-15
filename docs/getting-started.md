I want t# Getting Started

This guide will help you get started with OWL Server. We'll walk through the basic setup and common operations.

## Installation

You can install OWL Server using pip:

```bash
pip install owl-server
```

For development purposes, you can install directly from the repository:

```bash
pip install -e ".[dev]"
```

## Basic Usage

### Initializing the API

```python
from owl_mcp.owl_api import SimpleOwlAPI

# Initialize with an existing file
api = SimpleOwlAPI("path/to/ontology.owl")

# Or create a new ontology file
api = SimpleOwlAPI("new-ontology.owl", create_if_not_exists=True)
```

### Working with Prefixes

```python
# Add standard prefixes
api.add_prefix("owl", "http://www.w3.org/2002/07/owl#")
api.add_prefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
api.add_prefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
api.add_prefix("xsd", "http://www.w3.org/2001/XMLSchema#")

# Add a custom prefix
api.add_prefix("ex", "http://example.org/")
```

### Adding and Removing Axioms

```python
# Add an axiom in OWL functional syntax
api.add_axiom("ClassAssertion(ex:Person ex:John)")
api.add_axiom("SubClassOf(ex:Student ex:Person)")
api.add_axiom("ObjectPropertyAssertion(ex:knows ex:John ex:Jane)")

# Remove an axiom
api.remove_axiom("ClassAssertion(ex:Person ex:John)")
```

### Finding Axioms

```python
# Find all axioms containing a string
axioms = api.find_axioms("ex:Person")

# Find axioms of a specific type
class_axioms = api.find_axioms(pattern=None, axiom_type="ClassAssertion")

# Find axioms of a specific type with a pattern
john_class_axioms = api.find_axioms("ex:John", "ClassAssertion")
```

### Observing Changes

```python
# Define a change handler
def on_change(event_type, **kwargs):
    print(f"Event: {event_type}")
    if event_type == "axiom_added":
        print(f"Added axiom: {kwargs['axiom_str']}")
    elif event_type == "axiom_removed":
        print(f"Removed axiom: {kwargs['axiom_str']}")
    elif event_type == "prefix_added":
        print(f"Added prefix: {kwargs['prefix']} -> {kwargs['uri']}")
    elif event_type == "file_changed":
        print("File was changed externally")

# Register the observer
api.add_observer(on_change)

# Later, remove the observer
api.remove_observer(on_change)
```

### Cleanup

```python
# Always call stop() when done to release resources
api.stop()
```

## Next Steps

For more detailed information, check out the [API Reference](user-guide/api-reference.md) section or the [Examples](user-guide/basic-usage.md#examples) in the User Guide.