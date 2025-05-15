# OWL Server

OWL Server is a Model-Context-Protocol (MCP) server for working with Web Ontology Language (OWL) ontologies. It provides standardized tools for interacting with OWL ontologies through the MCP protocol, enabling seamless integration with AI assistants and applications.

## What is the Model Context Protocol (MCP)?

The Model Context Protocol (MCP) is an open standard for connecting AI assistants to external tools and data sources. MCP provides a standardized way to expose functionality to large language models (LLMs) like Claude, GPT, and other AI systems.

Think of MCP as a "USB-C port for AI applications" - it provides a consistent interface that allows AI assistants to:

- Access external data (like OWL ontologies)
- Execute specific operations (like adding/removing axioms)
- Work with your data in a secure, controlled manner

By implementing the MCP protocol, OWL Server allows AI assistants to directly manipulate ontologies without needing custom integrations for each LLM platform.

## What is OWL?

The Web Ontology Language (OWL) is a semantic markup language for publishing and sharing ontologies on the web. OWL is designed to represent rich and complex knowledge about things, groups of things, and relations between things.

Key OWL concepts that OWL Server helps you manage:

- **Axioms**: Statements that define relationships between entities
- **Classes**: Sets or collections of individuals with similar properties
- **Properties**: Relationships between individuals or between individuals and data values
- **Individuals**: Objects in the domain being described

OWL Server simplifies working with these concepts by providing tools that work with axiom strings in OWL Functional Syntax, avoiding the need to understand complex object models.

## Key Features

- **MCP Server Integration**: Connect AI assistants directly to OWL ontologies using the standardized Model-Context-Protocol
- **Thread-safe operations**: All ontology operations are thread-safe, making it suitable for multi-user environments
- **File synchronization**: Changes to the ontology file on disk are automatically detected and synchronized
- **Event-based notifications**: Register observers to be notified of changes to the ontology
- **Simple string-based API**: Work with OWL axioms as strings in functional syntax without dealing with complex object models

## MCP Server Quick Start

Run the OWL Server as an MCP server directly from the command line:

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

OWL Server exposes the following MCP tools:

- `add_axiom`: Add an axiom to the ontology
- `remove_axiom`: Remove an axiom from the ontology
- `find_axioms`: Find axioms matching a pattern
- `get_all_axioms`: Get all axioms in the ontology
- `add_prefix`: Add a prefix mapping to the ontology
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
pip install owl-server
```

## License

This project is licensed under the terms of the MIT license.