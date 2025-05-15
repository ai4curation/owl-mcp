# Installation

This page covers how to install OWL Server and set it up for use as an MCP server.

## Requirements

- Python 3.10 or later
- [py-horned-owl](https://github.com/hotwire/py-horned-owl) for OWL ontology processing
- [watchdog](https://github.com/gorakhargosh/watchdog) for file monitoring
- [mcp](https://modelcontextprotocol.io) for the Model-Context-Protocol implementation

## Standard Installation

The simplest way to install OWL Server is via pip:

```bash
pip install owl-server
```

This will install all required dependencies, including the MCP Python SDK.

## MCP-Specific Installation

For optimal MCP server usage, make sure you have the latest MCP SDK installed:

```bash
pip install "mcp>=0.1.0"
```

## Development Installation

For development purposes, you can install the package with development dependencies:

```bash
# Clone the repository
git clone https://github.com/your-username/owl-server.git
cd owl-server

# Install the package with development dependencies
pip install -e ".[dev]"
```

## Using UV package manager

If you're using [UV](https://github.com/astral-sh/uv), which is recommended for faster dependency resolution:

```bash
# Install UV if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install OWL Server with MCP dependencies
uv pip install owl-server "mcp>=0.1.0"
```

Or for development:

```bash
uv pip install -e ".[dev]"
```

## Verifying MCP Server Installation

After installation, you can verify the MCP server functionality with:

```python
import asyncio
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client

async def verify_mcp_server():
    # Configure the OWL MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "owl_mcp.mcp_tools"]
    )
    
    # Connect to the server
    print("Connecting to OWL MCP server...")
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # List available tools to verify connection
                tools = await session.list_tools()
                print(f"MCP server connection successful!")
                print(f"Available tools: {[tool.name for tool in tools]}")
                
    except Exception as e:
        print(f"MCP server connection failed: {str(e)}")

# Run the verification
asyncio.run(verify_mcp_server())
```

## Running the MCP Server

Start the OWL MCP server from the command line:

```bash
python -m owl_mcp.mcp_tools
```

This runs the server using the stdio transport, suitable for subprocess-based MCP clients. The server will remain running until it receives a termination signal or the process is interrupted.

## MCP Client Dependencies

If you're developing a client application that will connect to the OWL MCP server, make sure to install the MCP client libraries:

```bash
pip install "mcp>=0.1.0"
```

For integration with AI frameworks like LangChain or LlamaIndex:

```bash
pip install "mcp[langchain]>=0.1.0"  # For LangChain integration
pip install "mcp[llamaindex]>=0.1.0"  # For LlamaIndex integration
```

## Optional Dependencies

OWL Server has optional dependencies for specific features:

- **Development**: For development tasks (testing, linting, documentation), install with the `dev` extra:
  ```bash
  pip install -e ".[dev]"
  ```

- **Performance**: For improved performance with larger ontologies:
  ```bash
  pip install "owl-server[performance]"
  ```

## Docker Installation

You can also run OWL Server as an MCP server using Docker:

```bash
# Build the Docker image
docker build -t owl-mcp-server .

# Run the MCP server
docker run -p 8000:8000 -v /path/to/ontologies:/ontologies owl-mcp-server
```

## Next Steps

- See the [MCP Client Usage](mcp-client-usage.md) guide for examples of connecting to the OWL MCP server
- Check the [API Reference](api-reference.md) for details on available MCP tools
- Review [Basic Usage](basic-usage.md) for core concepts and examples