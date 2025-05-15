# Configuration System

OWL-Server includes a configuration system that allows you to define named ontologies 
with consistent settings and metadata. This system provides an easier way to work
with frequently used ontologies and ensures consistency across sessions.

## Configuration File

The configuration is stored in YAML format at `~/.owl-mcp/config.yaml`. This file
is automatically created when you first use the OWL-Server.

A sample configuration file might look like this:

```yaml
ontologies:
  pizza:
    path: /path/to/pizza.owl
    metadata_axioms:
      - 'AnnotationAssertion(rdfs:label ont:PizzaOntology "Pizza Ontology")'
      - 'AnnotationAssertion(owl:versionInfo ont:PizzaOntology "1.0.0")'
    readonly: false
    description: A sample pizza ontology
    preferred_serialization: ofn
  
  go:
    path: /data/ontologies/go.owl
    metadata_axioms: []
    readonly: true
    description: Gene Ontology (read-only reference)
    preferred_serialization: owl

default_serialization: ofn
enable_auto_discovery: true
log_level: INFO
editor_command: vim
default_namespace: http://example.org/
```

## Configuration Fields

### Global Settings

- `default_serialization`: Default serialization format for OWL files
- `enable_auto_discovery`: Whether to automatically discover ontologies in common locations
- `log_level`: Log level for OWL-Server (DEBUG, INFO, WARNING, ERROR)
- `editor_command`: Command to use when opening ontologies in an external editor
- `default_namespace`: Default namespace for newly created ontologies

### Ontology Configuration

Each configured ontology has the following fields:

- `path`: Absolute path to the OWL file
- `metadata_axioms`: List of metadata axioms to apply to the ontology
- `readonly`: Whether the ontology is read-only
- `description`: Optional description of the ontology
- `preferred_serialization`: Preferred serialization format for this ontology

## Using the Configuration System

You can manage configurations in multiple ways:

1. **Directly editing the YAML file**: Edit `~/.owl-mcp/config.yaml` with a text editor
2. **Through MCP tools**: Use the configuration tools provided by the MCP server
3. **Programmatically**: Use the `ConfigManager` API in the `owl_mcp.config` module

## Accessing Configuration

There are multiple ways to work with the configuration system:

### MCP Configuration Tools

The following MCP tools are available for managing ontology configurations:

#### Managing Configurations

- `list_configured_ontologies()`: Lists all configured ontologies
- `configure_ontology(name, path, metadata_axioms=None, readonly=False, description=None, preferred_serialization=None)`: Adds or updates an ontology configuration
- `remove_ontology_config(name)`: Removes an ontology from the configuration
- `get_ontology_config(name)`: Gets configuration details for a specific ontology
- `register_ontology_in_config(owl_file_path, name=None, readonly=None, description=None, preferred_serialization=None)`: Registers an existing ontology in the configuration
- `load_and_register_ontology(owl_file_path, name=None, readonly=False, create_if_not_exists=True, description=None, preferred_serialization=None, metadata_axioms=None)`: Loads an ontology and registers it in the configuration in one step

#### API Methods

The `SimpleOwlAPI` class provides the following methods for working with configurations:

- `register_in_config(name=None, readonly=None, description=None, preferred_serialization=None)`: Registers the current ontology in the configuration system

#### Working with Named Ontologies

The following tools allow you to work with ontologies by name instead of path:

- `add_axiom_by_name(ontology_name, axiom_str)`: Adds an axiom to a named ontology
- `remove_axiom_by_name(ontology_name, axiom_str)`: Removes an axiom from a named ontology
- `find_axioms_by_name(ontology_name, pattern, limit=100)`: Finds axioms in a named ontology
- `add_prefix_by_name(ontology_name, prefix, uri)`: Adds a prefix to a named ontology

### MCP Resources

The following MCP resources allow direct access to configuration data:

- `resource://config/ontologies`: List of all configured ontologies
- `resource://config/ontology/{name}`: Details about a specific ontology configuration
- `resource://active`: List of all active OWL file paths

Example of using resources:

```python
from fastmcp import Client

async with Client("owl-server") as client:
    # Get all configured ontologies
    ontologies = await client.read_resource("resource://config/ontologies")
    
    # Print the names of all configured ontologies
    print("Configured ontologies:")
    for ontology in ontologies.value:
        print(f"- {ontology['name']}: {ontology['path']}")
        
    # Get details about a specific ontology
    pizza = await client.read_resource("resource://config/ontology/pizza")
    if pizza.value:
        print(f"Pizza ontology at: {pizza.value['path']}")
        print(f"Read-only: {pizza.value['readonly']}")
        
    # Get list of active ontologies
    active = await client.read_resource("resource://active")
    print(f"Active ontologies: {len(active.value)}")
```

## Readonly Ontologies

When an ontology is marked as readonly, the following behavior applies:

1. Attempts to add, remove, or modify axioms will be rejected
2. Changes to the in-memory representation are allowed, but will not be saved to disk
3. This is useful for reference ontologies that shouldn't be modified

## Metadata Axioms

The metadata_axioms field allows you to define ontology-level metadata that will be 
automatically added when the ontology is loaded. This is useful for:

1. Ensuring consistent metadata across sessions
2. Adding standard annotations to all ontologies
3. Setting version information, labels, and other metadata

Metadata axioms are specified in OWL functional syntax, typically as annotation assertions.

## Examples

### Example 1: Configuring and Using a Named Ontology

Here's an example of how to configure and use a named ontology through MCP:

```python
from fastmcp import Client

async with Client("owl-server") as client:
    # Configure a new ontology
    await client.call_tool("configure_ontology", {
        "name": "pizza",
        "path": "/path/to/pizza.owl",
        "metadata_axioms": [
            'AnnotationAssertion(rdfs:label ont:PizzaOntology "Pizza Ontology")',
            'AnnotationAssertion(owl:versionInfo ont:PizzaOntology "1.0.0")'
        ],
        "description": "A sample pizza ontology"
    })
    
    # Now use it by name (no need to remember the path)
    await client.call_tool("add_axiom_by_name", {
        "ontology_name": "pizza",
        "axiom_str": "Declaration(Class(pizza:VegetarianPizza))"
    })
    
    # Find axioms by pattern
    results = await client.call_tool("find_axioms_by_name", {
        "ontology_name": "pizza",
        "pattern": "Vegetarian"
    })
    
    print(f"Found {len(results)} axioms about vegetarian pizzas")
```

### Example 2: Loading and Registering in One Step

Here's an example of using the `load_and_register_ontology` tool:

```python
from fastmcp import Client

async with Client("owl-server") as client:
    # Load and register a new ontology in one step
    result = await client.call_tool("load_and_register_ontology", {
        "owl_file_path": "/data/ontologies/gene_ontology.owl",
        "name": "go",
        "readonly": True,
        "description": "Gene Ontology (read-only reference)",
        "metadata_axioms": [
            'AnnotationAssertion(rdfs:label ont:GO "Gene Ontology")',
            'AnnotationAssertion(owl:versionInfo ont:GO "2023-05-14")'
        ]
    })
    
    print(result)  # "Loaded and registered ontology 'go' at /data/ontologies/gene_ontology.owl"
    
    # Now use it by name
    axioms = await client.call_tool("find_axioms_by_name", {
        "ontology_name": "go",
        "pattern": "mitochondr"
    })
    
    print(f"Found {len(axioms)} axioms related to mitochondria")
```

### Example 3: Registering an Open Ontology

Here's an example of using the API directly to register an ontology that's already loaded:

```python
from owl_mcp.owl_api import SimpleOwlAPI
from owl_mcp.config import get_config_manager

# First load an ontology
api = SimpleOwlAPI("/path/to/ontology.owl")

# Add some axioms
api.add_axiom("Declaration(Class(ex:MyClass))")
api.add_axiom("SubClassOf(ex:MyClass owl:Thing)")

# Now register it in the configuration
name = api.register_in_config(
    name="my-ontology",
    description="My custom ontology",
    readonly=False
)

print(f"Registered as '{name}' in configuration")

# Verify it's in the configuration
config_manager = get_config_manager()
print(config_manager.get_ontology("my-ontology"))
```

Using named ontologies makes it much easier to work with frequently used ontologies,
as you no longer need to remember or type long file paths.