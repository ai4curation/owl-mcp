# OWL-MCP

OWL-MCP is a Model-Context-Protocol (MCP) server for working with Web Ontology Language (OWL) ontologies. It provides standardized tools for interacting with OWL ontologies through the MCP protocol, enabling seamless integration with AI assistants and applications.

## Goose Install

[Install](goose://extension?cmd=uvx&arg=owl-mcp&id=owl_mcp&name=OWL%20MCP)


## What is the Model Context Protocol (MCP)?

The Model Context Protocol (MCP) is an open standard for connecting AI assistants to external tools and data sources. MCP provides a standardized way to expose functionality to large language models (LLMs) like Claude, GPT, and other AI systems.

Think of MCP as a "USB-C port for AI applications" - it provides a consistent interface that allows AI assistants to:

- Access external data (like OWL ontologies)
- Execute specific operations (like adding/removing axioms)
- Work with your data in a secure, controlled manner

By implementing the MCP protocol, OWL-MCP allows AI assistants to directly manipulate ontologies without needing custom integrations for each LLM platform.

## What is OWL?

The Web Ontology Language (OWL) is a semantic markup language for publishing and sharing ontologies on the web. OWL is designed to represent rich and complex knowledge about things, groups of things, and relations between things.

Key OWL concepts that OWL-MCP helps you manage:

- **Axioms**: Statements that define relationships between entities
- **Classes**: Sets or collections of individuals with similar properties
- **Properties**: Relationships between individuals or between individuals and data values
- **Individuals**: Objects in the domain being described

OWL-MCP simplifies working with these concepts by providing tools that work with axiom strings in OWL Functional Syntax, avoiding the need to understand complex object models.

## Key Features

- **MCP Server Integration**: Connect AI assistants directly to OWL ontologies using the standardized Model-Context-Protocol
- **Thread-safe operations**: All ontology operations are thread-safe, making it suitable for multi-user environments
- **File synchronization**: Changes to the ontology file on disk are automatically detected and synchronized
- **Event-based notifications**: Register observers to be notified of changes to the ontology
- **Simple string-based API**: Work with OWL axioms as strings in functional syntax without dealing with complex object models
- **Configuration system**: Store and manage settings for frequently-used ontologies
- **Label support**: Access human-readable labels for entities with configurable annotation properties

## MCP Server Quick Start

Run the OWL-MCP server directly from the command line:

```bash
# Run the MCP server with stdio transport
uvx run owl-mcp
```

Or integrate within your application:

```python
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp import ClientSession

# Start the OWL MCP server
server_params = StdioServerParameters(
    command="python",
    args=["-m", "owl_mcp.mcp_tools"]
)

# Connect an MCP client
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        
        # Use MCP tools to work with OWL ontologies
        result = await session.invoke_tool(
            "add_axiom", 
            {"owl_file_path": "/path/to/ontology.owl", 
             "axiom_str": "SubClassOf(:Dog :Animal)"}
        )
        print(result)
        
        # Find axioms matching a pattern
        axioms = await session.invoke_tool(
            "find_axioms",
            {"owl_file_path": "/path/to/ontology.owl",
             "pattern": "Dog"}
        )
        print(axioms)
```

## Available MCP Tools

OWL-MCP exposes the following MCP tools:

- `add_axiom`: Add an axiom to the ontology
- `remove_axiom`: Remove an axiom from the ontology
- `find_axioms`: Find axioms matching a pattern (with optional labels)
- `get_all_axioms`: Get all axioms in the ontology (with optional labels)
- `add_prefix`: Add a prefix mapping to the ontology
- `get_labels_for_iri`: Get human-readable labels for an IRI
- `get_labels_for_iri_by_name`: Get labels for an IRI in a configured ontology
- `configure_ontology`: Add or update an ontology in the configuration
- `register_ontology_in_config`: Register an existing ontology in the configuration system
- `load_and_register_ontology`: Load an ontology and register it in the configuration
- `list_configured_ontologies`: List all ontologies defined in the configuration
- `get_ontology_config`: Get configuration for a specific ontology
- `remove_ontology_config`: Remove an ontology from the configuration
- `list_active_owl_files`: List all OWL files currently being managed

## Core API Example

The server is built on a core API that can also be used directly:

```python
from owl_mcp.owl_api import SimpleOwlAPI

# Initialize the API
api = SimpleOwlAPI("my-ontology.owl")

# Add a prefix
api.add_prefix("ex:", "http://example.org/")

# Add an axiom
api.add_axiom("ClassAssertion(ex:Person ex:John)")

# Find axioms
axioms = api.find_axioms(":John")
for axiom in axioms:
    print(axiom)
```

## Installation

```bash
pip install owl-mcp
```

## Advanced Features

### Configuration System

OWL-MCP includes a configuration system that stores ontology metadata and settings in `~/.owl-mcp/config.yaml`. This allows you to:

- Define named ontologies with paths and metadata
- Set ontologies as readonly to prevent modifications
- Add default metadata axioms to ontologies
- Specify preferred serialization formats
- Configure annotation properties for labels

### Label Support

OWL-MCP provides built-in support for retrieving and displaying human-readable labels alongside entity IRIs:

```python
from owl_mcp.owl_api import SimpleOwlAPI

# Initialize API with custom annotation property for labels
api = SimpleOwlAPI("my-ontology.owl", annotation_property="http://www.w3.org/2004/02/skos/core#prefLabel")

# Get all axioms with human-readable labels
axioms = api.get_all_axiom_strings(include_labels=True)
for axiom in axioms:
    print(axiom)
    # Output: SubClassOf(ex:Dog ex:Animal) ## ex:Dog = "Dog"; ex:Animal = "Animal"
```

## License

This project is licensed under the terms of the MIT license.