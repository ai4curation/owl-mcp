# OWL Server

A simple server for OWL operations that provides a clean API for managing OWL ontologies.

## Features

- Add and remove axioms
- Find axioms by pattern
- Manage prefix mappings
- Event-based change notifications
- Simple command-line interface

## Installation

```bash
pip install -e .
```

## Usage

### Initialize a new OWL file

```bash
python -m owl_server.server init my-ontology.owl
```

### Start the server

```bash
python -m owl_server.server start my-ontology.owl --debug
```

### Python API

```python
from owl_mcp.owl_api import OwlAPI

# Initialize the API
api = OwlAPI("my-ontology.owl")

# Add an axiom
api.add_axiom("ClassAssertion(:Person :John)")

# Find axioms
axioms = api.find_axioms(":John")

# Add a prefix
api.add_prefix("ex:", "http://example.org/")


# Register for changes
def on_change(event_type, **kwargs):
   print(f"Change: {event_type}", kwargs)


api.add_observer(on_change)
```

## Development

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install development dependencies: `pip install -e ".[dev]"`