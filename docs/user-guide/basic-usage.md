# Basic Usage

This guide covers common usage patterns and examples for the OWL Server library.

## Core Concepts

OWL Server is built around a few key concepts:

1. **SimpleOwlAPI**: The main interface for working with OWL ontologies
2. **Thread Safety**: All operations are guarded by locks for concurrent access
3. **File Monitoring**: Changes to files on disk are detected automatically
4. **Observer Pattern**: Register callbacks to be notified of changes
5. **Functional Syntax**: Work with axioms in OWL functional syntax as strings

## Creating and Opening Ontologies

### Creating a New Ontology

```python
from owl_mcp.owl_api import SimpleOwlAPI

# Create a new ontology file
api = SimpleOwlAPI("new-ontology.owl", create_if_not_exists=True)

# Add some standard prefixes
api.add_prefix("owl", "http://www.w3.org/2002/07/owl#")
api.add_prefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
api.add_prefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
api.add_prefix("xsd", "http://www.w3.org/2001/XMLSchema#")
api.add_prefix("ex", "http://example.org/")
```

### Opening an Existing Ontology

```python
from owl_mcp.owl_api import SimpleOwlAPI

# Open an existing ontology file
api = SimpleOwlAPI("existing-ontology.owl")
```

### Specifying Serialization Format

```python
from owl_mcp.owl_api import SimpleOwlAPI

# Open with a specific serialization format
api = SimpleOwlAPI("ontology.owl", serialization="rdfxml")
```

## Working with Axioms

### Adding Axioms

```python
# Add class axioms
api.add_axiom("Declaration(Class(ex:Person))")
api.add_axiom("Declaration(Class(ex:Student))")
api.add_axiom("SubClassOf(ex:Student ex:Person)")

# Add individual axioms
api.add_axiom("Declaration(NamedIndividual(ex:John))")
api.add_axiom("ClassAssertion(ex:Person ex:John)")

# Add object property axioms
api.add_axiom("Declaration(ObjectProperty(ex:knows))")
api.add_axiom("ObjectPropertyAssertion(ex:knows ex:John ex:Jane)")
```

### Removing Axioms

```python
# Remove an axiom
api.remove_axiom("ClassAssertion(ex:Person ex:John)")
```

### Finding Axioms

```python
# Get all axioms
all_axioms = api.get_all_axiom_strings()
for axiom in all_axioms:
    print(axiom)

# Find axioms containing a pattern
person_axioms = api.find_axioms("ex:Person")
for axiom in person_axioms:
    print(axiom)

# Find axioms of a specific type
class_axioms = api.find_axioms(pattern=None, axiom_type="ClassAssertion")

# Combine pattern and type
student_class_axioms = api.find_axioms("ex:Student", "SubClassOf")
```

## Managing Prefixes

```python
# Add a prefix
api.add_prefix("ex", "http://example.org/")

# Add multiple prefixes
prefixes = {
    "foaf": "http://xmlns.com/foaf/0.1/",
    "dc": "http://purl.org/dc/elements/1.1/"
}
for prefix, uri in prefixes.items():
    api.add_prefix(prefix, uri)
```

## Observing Changes

The observer pattern allows you to register callbacks that will be notified of changes to the ontology.

### Event Types

- `axiom_added`: Fired when an axiom is added
- `axiom_removed`: Fired when an axiom is removed
- `prefix_added`: Fired when a prefix is added
- `file_changed`: Fired when the file is changed externally

### Registering Observers

```python
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

# Make some changes
api.add_axiom("ClassAssertion(ex:Person ex:Alice)")  # Triggers axiom_added event

# Later, remove the observer
api.remove_observer(on_change)
```

## File Synchronization

OWL Server automatically monitors the ontology file for changes and synchronizes the in-memory representation with the file on disk. This is useful in collaborative environments where multiple processes might be modifying the same file.

```python
# Changes made to the file by external processes are automatically detected
# and the in-memory ontology is synchronized

# To manually trigger synchronization
api.sync_with_file()
```

## Resource Management

Always call `stop()` when done with the API to release resources, particularly the file monitoring threads:

```python
# Clean up resources
api.stop()
```

## Complete Example

Here's a complete example showing the main features:

```python
from owl_mcp.owl_api import SimpleOwlAPI

# Create or open an ontology
api = SimpleOwlAPI("university.owl", create_if_not_exists=True)

# Add prefixes
api.add_prefix("owl", "http://www.w3.org/2002/07/owl#")
api.add_prefix("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
api.add_prefix("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
api.add_prefix("xsd", "http://www.w3.org/2001/XMLSchema#")
api.add_prefix("univ", "http://example.org/university#")

# Define a change listener
def on_change(event_type, **kwargs):
    print(f"Event: {event_type}")
    if event_type == "axiom_added":
        print(f"Added: {kwargs['axiom_str']}")
    elif event_type == "axiom_removed":
        print(f"Removed: {kwargs['axiom_str']}")

# Register the observer
api.add_observer(on_change)

# Add class hierarchy
api.add_axiom("Declaration(Class(univ:Person))")
api.add_axiom("Declaration(Class(univ:Student))")
api.add_axiom("Declaration(Class(univ:Professor))")
api.add_axiom("SubClassOf(univ:Student univ:Person)")
api.add_axiom("SubClassOf(univ:Professor univ:Person)")

# Add properties
api.add_axiom("Declaration(ObjectProperty(univ:teaches))")
api.add_axiom("Declaration(ObjectProperty(univ:enrolledIn))")
api.add_axiom("Declaration(DataProperty(univ:name))")
api.add_axiom("Declaration(DataProperty(univ:studentId))")

# Add individuals
api.add_axiom("Declaration(NamedIndividual(univ:John))")
api.add_axiom("ClassAssertion(univ:Professor univ:John)")
api.add_axiom("Declaration(NamedIndividual(univ:CS101))")
api.add_axiom("ObjectPropertyAssertion(univ:teaches univ:John univ:CS101)")

# Find all professors
professors = api.find_axioms("univ:Professor", "ClassAssertion")
print("\nProfessors:")
for p in professors:
    print(f"- {p}")

# Find all courses taught by John
john_courses = api.find_axioms("univ:John", "ObjectPropertyAssertion")
print("\nJohn's courses:")
for c in john_courses:
    print(f"- {c}")

# Clean up
api.stop()
```

## Next Steps

For more detailed information about the API, see the [API Reference](api-reference.md) section.