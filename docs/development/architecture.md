# Architecture

This document provides an overview of the architecture of the OWL Server, focusing on its Model-Context-Protocol (MCP) integration.

## High-Level Architecture

OWL Server is designed with a layered architecture, with MCP as the primary interface:

```
+--------------------------------------+
|                                      |
|       MCP Server & Tools Layer       |
|                                      |
+--------------------------------------+
                  |
+--------------------------------------+
|                                      |
|           SimpleOwlAPI               |
|                                      |
+--------------------------------------+
                  |
+--------------------------------------+
|                                      |
|           py-horned-owl              |
|                                      |
+--------------------------------------+
```

1. **py-horned-owl Layer**: The foundation that provides OWL ontology operations.
2. **SimpleOwlAPI Layer**: A simplified API on top of py-horned-owl with file synchronization and observer pattern.
3. **MCP Server & Tools Layer**: The primary interface exposing ontology operations through the standardized Model-Context-Protocol.

## MCP Server Architecture

The MCP server is the core component of OWL Server, enabling AI assistants and applications to interact with OWL ontologies:

```
+-----------------------------------+
|                                   |
|      AI Assistant / LLM           |
|                                   |
+-----------------+-----------------+
                  |
                  | MCP Protocol
                  |
+-----------------v-----------------+
|                                   |
|      OWL Server (MCP Server)      |
|                                   |
+-----------------+-----------------+
                  |
                  | File I/O
                  |
+-----------------v-----------------+
|                                   |
|        OWL Ontology Files         |
|                                   |
+-----------------------------------+
```

The MCP server:

1. Exposes standardized tools for ontology manipulation
2. Maintains thread-safety for concurrent operations
3. Handles file synchronization automatically
4. Manages instance caching for performance

## Core Components

### MCP Server Implementation

The MCP server is implemented using the `FastMCP` library, which provides a framework for creating Model-Context-Protocol servers:

```python
from mcp.server.fastmcp import FastMCP

# Initialize MCP server with a name and instructions
mcp = FastMCP("owl-server", instructions="""
OWL Server provides tools for managing Web Ontology Language (OWL) ontologies.
Use these tools to add, remove, and find axioms in OWL files, and to manage prefix mappings.

The tools operate on OWL files specified by absolute paths.
""")

# Define MCP tools using decorators
@mcp.tool()
async def add_axiom(owl_file_path: str, axiom_str: str) -> str:
    # Implementation...
```

### MCP Tools and Prompts

The OWL Server exposes the following MCP components:

#### MCP Tools

MCP tools are functions that can be invoked by clients to perform operations:

- `add_axiom`: Add an axiom to an ontology file
- `remove_axiom`: Remove an axiom from an ontology file
- `find_axioms`: Find axioms in an ontology file
- `get_all_axioms`: Get all axioms from an ontology file
- `add_prefix`: Add a prefix mapping to an ontology file
- `list_active_owl_files`: List all active ontology files

#### MCP Prompts

MCP prompts provide reusable templates for LLM interactions:

- `ask_for_axioms_about`: Generates a prompt asking for explanations about ontology concepts

### SimpleOwlAPI

The `SimpleOwlAPI` class serves as the middleware between MCP tools and the underlying OWL operations:

- Thread-safe operations on OWL ontologies
- File synchronization with watchdog
- Observer pattern for change notifications
- String-based axiom manipulation

#### Key Methods

- `add_axiom()`: Add an axiom to the ontology
- `remove_axiom()`: Remove an axiom from the ontology
- `find_axioms()`: Find axioms matching a pattern
- `get_all_axiom_strings()`: Get all axioms as strings
- `add_prefix()`: Add a prefix mapping to the ontology
- `sync_with_file()`: Synchronize in-memory representation with file on disk
- `add_observer()` / `remove_observer()`: Manage change observers

### Axiom Parser

The `axiom_parser` module handles the conversion between string representations of OWL axioms and the py-horned-owl objects.

Key functions:

- `parse_axiom_string()`: Parse a string into py-horned-owl axiom objects
- `axiom_to_string()`: Convert a py-horned-owl axiom to a string
- `serialize_axioms()`: Serialize a list of axioms to strings

## MCP Communication Flow

The typical communication flow when using OWL Server through MCP:

1. **Client Connection**:
   ```
   AI Assistant/Client -> MCP Protocol -> OWL Server
   ```

2. **Tool Invocation**:
   ```
   Client -> MCP Tool Request -> OWL Server -> SimpleOwlAPI -> File System
   ```

3. **Response Flow**:
   ```
   File System -> SimpleOwlAPI -> MCP Server -> MCP Protocol -> Client
   ```

Example sequence diagram for adding an axiom:

```
Client            MCP Server           SimpleOwlAPI         File System
  |                   |                      |                   |
  |---- invoke ------>|                      |                   |
  |  add_axiom()      |                      |                   |
  |                   |---- add_axiom() ---->|                   |
  |                   |                      |---- write ------->|
  |                   |                      |<---- confirm -----|
  |                   |<---- success --------|                   |
  |<---- result ------|                      |                   |
```

## Instance Management

OWL Server implements efficient instance management for MCP tools:

```python
# Dictionary to cache SimpleOwlAPI instances
_api_instances = {}

def _get_api_instance(owl_file_path: str) -> SimpleOwlAPI:
    """Get or create a SimpleOwlAPI instance for the given file path."""
    owl_file_path = os.path.abspath(owl_file_path)
    
    if owl_file_path not in _api_instances:
        _api_instances[owl_file_path] = SimpleOwlAPI(owl_file_path)
        
    return _api_instances[owl_file_path]
```

This caching mechanism ensures:

1. Only one API instance per file path
2. Consistent state across multiple MCP tool invocations
3. Efficient resource usage

## Design Patterns

### Observer Pattern

The observer pattern is used to notify clients of changes to the ontology:

1. Clients register callback functions using `add_observer()`
2. When changes occur, registered callbacks are notified with event information
3. Clients can unregister using `remove_observer()`

### Thread Safety

All operations on the ontology are guarded by a reentrant lock to ensure thread safety:

```python
with self.lock:
    # Perform operations on the ontology
```

### File Monitoring

File monitoring is implemented using the watchdog library:

1. An `Observer` watches the directory containing the ontology file
2. When changes are detected, the `sync_with_file()` method is called
3. This synchronizes the in-memory representation with the file on disk

## Performance Considerations

- **File Operations**: File operations are minimized to improve performance
- **Locking**: The lock is acquired only when necessary to minimize contention
- **Hash Checking**: File hashes are used to detect changes, avoiding unnecessary reloads
- **Instance Caching**: MCP tools cache API instances to avoid recreating them for each call
- **Asynchronous Operations**: MCP tools are implemented as async functions for better performance in concurrent environments