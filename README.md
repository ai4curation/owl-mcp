# OWL-MCP

[![PyPI version](https://img.shields.io/pypi/v/owl-mcp.svg)](https://pypi.org/project/owl-mcp/)
[![Python Versions](https://img.shields.io/pypi/pyversions/owl-mcp.svg)](https://pypi.org/project/owl-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/github/actions/workflow/status/cmungall/owl-server/test.yml?branch=main&label=tests)](https://github.com/cmungall/owl-server/actions)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://cmungall.github.io/owl-server)

A Model-Context-Protocol (MCP) server for managing Web Ontology Language (OWL) ontologies, providing a simplified API for ontology operations.

## Goose Install

[Install](goose://extension?cmd=uvx&arg=owl-mcp&id=owl_mcp&name=OWL%20MCP)

## What is OWL-MCP?

OWL-MCP is a server that implements the Model-Context-Protocol (MCP) for working with OWL ontologies. It provides standardized tools for interacting with ontologies through the MCP protocol, enabling seamless integration with AI assistants and applications.

MCP is an open standard for connecting AI assistants to external tools and data sources, providing a consistent interface that allows AI systems to access and manipulate OWL ontologies without requiring custom integrations.

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
        
        # Find axioms matching a pattern with labels
        axioms = await session.invoke_tool(
            "find_axioms",
            {"owl_file_path": "/path/to/ontology.owl",
             "pattern": "Dog",
             "include_labels": True}
        )
        print(axioms)
```

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

# Find axioms with human-readable labels
axioms = api.find_axioms(":John", include_labels=True)
for axiom in axioms:
    print(axiom)
    # Output: ClassAssertion(ex:Person ex:John) ## ex:Person = "Person"; ex:John = "John"
```

## Available MCP Tools

OWL-MCP exposes the following MCP tools:

- `add_axiom`: Add an axiom to the ontology
- `remove_axiom`: Remove an axiom from the ontology
- `find_axioms`: Find axioms matching a pattern (with optional labels)
- `get_all_axioms`: Get all axioms in the ontology (with optional labels)
- `add_prefix`: Add a prefix mapping to the ontology
- `get_labels_for_iri`: Get human-readable labels for an IRI
- `configure_ontology`: Add or update an ontology in the configuration
- `register_ontology_in_config`: Register an existing ontology in the configuration system
- `list_configured_ontologies`: List all ontologies defined in the configuration
- `list_active_owl_files`: List all OWL files currently being managed

## Installation

```bash
pip install owl-mcp
```

## Development

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Unix/MacOS: `source .venv/bin/activate`
4. Install development dependencies: `make install`
5. Run tests: `make test`

## Documentation

For more information, see the [full documentation](https://cmungall.github.io/owl-server).

## License

This project is licensed under the terms of the MIT license.