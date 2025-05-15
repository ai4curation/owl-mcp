# API Reference

This page documents the main classes and methods of the OWL Server, with a focus on its MCP (Model-Context-Protocol) tools and API.

## MCP Server

OWL Server primarily functions as an MCP server that exposes tools for interacting with OWL ontologies. These tools can be accessed by any MCP client, including AI assistants like Claude and GPT.

### Running the MCP Server

To run the OWL Server as an MCP server:

```bash
python -m owl_mcp.mcp_tools
```

This starts the server using the stdio transport, which is suitable for subprocess-based MCP clients.

### MCP Client Connection

Use the Python MCP client library to connect to the OWL Server:

```python
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client

# Configure the OWL MCP server
server_params = StdioServerParameters(
    command="python",
    args=["-m", "owl_mcp.mcp_tools"]
)

# Connect to the server
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        
        # Now you can invoke MCP tools
        # ...
```

## MCP Tools Reference

The following MCP tools are exposed by the OWL Server for interacting with OWL ontologies.

### `add_axiom`

```python
async def add_axiom(owl_file_path: str, axiom_str: str) -> str
```

Adds an axiom to the ontology using OWL functional syntax.

**Parameters:**

- `owl_file_path` (str): Absolute path to the OWL file
- `axiom_str` (str): String representation of the axiom in OWL functional syntax, e.g., "SubClassOf(:Dog :Animal)"

**Returns:**

- `str`: Success message or error

**Example:**

```python
result = await session.invoke_tool("add_axiom", {
    "owl_file_path": "/path/to/ontology.owl",
    "axiom_str": "SubClassOf(:Dog :Animal)"
})
print(result)  # "Successfully added axiom: SubClassOf(:Dog :Animal)"
```

---

### `remove_axiom`

```python
async def remove_axiom(owl_file_path: str, axiom_str: str) -> str
```

Removes an axiom from the ontology using OWL functional syntax.

**Parameters:**

- `owl_file_path` (str): Absolute path to the OWL file
- `axiom_str` (str): String representation of the axiom in OWL functional syntax

**Returns:**

- `str`: Success message or error

**Example:**

```python
result = await session.invoke_tool("remove_axiom", {
    "owl_file_path": "/path/to/ontology.owl",
    "axiom_str": "SubClassOf(:Dog :Animal)"
})
print(result)  # "Successfully removed axiom: SubClassOf(:Dog :Animal)"
```

---

### `find_axioms`

```python
async def find_axioms(owl_file_path: str, pattern: str, limit: int = 100) -> List[str]
```

Finds axioms matching a pattern in the ontology.

**Parameters:**

- `owl_file_path` (str): Absolute path to the OWL file
- `pattern` (str): A string pattern to match against axiom strings (simple substring matching)
- `limit` (int, optional): Maximum number of axioms to return. Defaults to 100.

**Returns:**

- `List[str]`: List of matching axiom strings

**Example:**

```python
axioms = await session.invoke_tool("find_axioms", {
    "owl_file_path": "/path/to/ontology.owl",
    "pattern": "Dog",
    "limit": 50
})
for axiom in axioms:
    print(axiom)
```

---

### `get_all_axioms`

```python
async def get_all_axioms(owl_file_path: str, limit: int = 100) -> List[str]
```

Gets all axioms in the ontology as strings.

**Parameters:**

- `owl_file_path` (str): Absolute path to the OWL file
- `limit` (int, optional): Maximum number of axioms to return. Defaults to 100.

**Returns:**

- `List[str]`: List of all axiom strings

**Example:**

```python
axioms = await session.invoke_tool("get_all_axioms", {
    "owl_file_path": "/path/to/ontology.owl",
    "limit": 200
})
print(f"Ontology contains {len(axioms)} axioms")
```

---

### `add_prefix`

```python
async def add_prefix(owl_file_path: str, prefix: str, uri: str) -> str
```

Adds a prefix mapping to the ontology.

**Parameters:**

- `owl_file_path` (str): Absolute path to the OWL file
- `prefix` (str): The prefix string (e.g., "ex:")
- `uri` (str): The URI the prefix maps to (e.g., "http://example.org/")

**Returns:**

- `str`: Success message or error

**Example:**

```python
result = await session.invoke_tool("add_prefix", {
    "owl_file_path": "/path/to/ontology.owl",
    "prefix": "ex:",
    "uri": "http://example.org/"
})
print(result)  # "Successfully added prefix mapping: ex: -> http://example.org/"
```

---

### `list_active_owl_files`

```python
async def list_active_owl_files() -> List[str]
```

Lists all OWL files currently being managed by the MCP server.

**Returns:**

- `List[str]`: List of file paths for active OWL files

**Example:**

```python
active_files = await session.invoke_tool("list_active_owl_files", {})
for file_path in active_files:
    print(f"Active OWL file: {file_path}")
```

## Core API (SimpleOwlAPI)

The MCP server is built on top of the `SimpleOwlAPI` class, which can be used directly if you prefer to work with OWL ontologies without the MCP protocol.

### Constructor

```python
SimpleOwlAPI(owl_file_path: str, create_if_not_exists: bool = True, serialization: Optional[str] = None)
```

**Parameters:**

- `owl_file_path` (str): Path to the OWL file
- `create_if_not_exists` (bool, optional): Whether to create the file if it doesn't exist. Defaults to True.
- `serialization` (str, optional): Serialization format (e.g., "ofn", "owl", "rdfxml"). If not specified, it will be inferred from the file extension or content.

### Key Methods

#### `add_axiom`

```python
add_axiom(axiom_str: str) -> bool
```

Adds an axiom to the ontology using OWL functional syntax.

#### `remove_axiom`

```python
remove_axiom(axiom_str: str) -> bool
```

Removes an axiom from the ontology.

#### `find_axioms`

```python
find_axioms(pattern: Optional[str], axiom_type: Optional[str] = None) -> List[str]
```

Finds axioms matching a pattern in the ontology.

#### `get_all_axiom_strings`

```python
get_all_axiom_strings() -> List[str]
```

Gets all axioms in the ontology as strings.

#### `add_prefix`

```python
add_prefix(prefix: str, uri: str) -> bool
```

Adds a prefix mapping to the ontology.

#### `add_observer` / `remove_observer`

```python
add_observer(callback: Callable) -> None
remove_observer(callback: Callable) -> None
```

Adds or removes an observer to be notified of ontology changes.

#### `stop`

```python
stop() -> None
```

Stops the API and releases resources, particularly the file monitoring thread.

For complete details on the `SimpleOwlAPI` methods, see the [source code](/src/owl_mcp/owl_api.py).