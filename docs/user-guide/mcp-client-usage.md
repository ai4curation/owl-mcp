# MCP Client Usage

This guide provides examples of how to use OWL Server through the Model Context Protocol (MCP) from different client environments.

## What is MCP?

The Model Context Protocol (MCP) is an open standard for connecting AI assistants to external tools and data sources. It provides a standardized way for applications to expose functionality to large language models (LLMs) and other AI systems.

OWL Server implements MCP, allowing you to:

- Connect AI assistants directly to OWL ontologies
- Perform ontology operations through a standardized interface
- Integrate with any MCP-compatible client

## Basic MCP Client Connection

The following example demonstrates how to connect to the OWL Server using the Python MCP client library:

```python
import asyncio
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client

async def connect_to_owl_server():
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
            
    print("Connection closed")

# Run the async function
asyncio.run(connect_to_owl_server())
```

## Complete Working Example

Here's a complete example that demonstrates creating a new ontology, adding prefixes and axioms, and querying the ontology:

```python
import asyncio
import os
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client

async def owl_example():
    # Create a temporary ontology file
    temp_owl_file = os.path.abspath("example.owl")
    
    # Configure the OWL MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "owl_mcp.mcp_tools"]
    )
    
    # Connect to the server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Add standard prefixes
            await session.invoke_tool("add_prefix", {
                "owl_file_path": temp_owl_file,
                "prefix": "owl:",
                "uri": "http://www.w3.org/2002/07/owl#"
            })
            
            await session.invoke_tool("add_prefix", {
                "owl_file_path": temp_owl_file,
                "prefix": "rdf:",
                "uri": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            })
            
            await session.invoke_tool("add_prefix", {
                "owl_file_path": temp_owl_file,
                "prefix": "ex:",
                "uri": "http://example.org/"
            })
            
            # Add classes and individuals
            await session.invoke_tool("add_axiom", {
                "owl_file_path": temp_owl_file,
                "axiom_str": "Declaration(Class(ex:Animal))"
            })
            
            await session.invoke_tool("add_axiom", {
                "owl_file_path": temp_owl_file,
                "axiom_str": "Declaration(Class(ex:Dog))"
            })
            
            await session.invoke_tool("add_axiom", {
                "owl_file_path": temp_owl_file,
                "axiom_str": "SubClassOf(ex:Dog ex:Animal)"
            })
            
            await session.invoke_tool("add_axiom", {
                "owl_file_path": temp_owl_file,
                "axiom_str": "Declaration(NamedIndividual(ex:Fido))"
            })
            
            await session.invoke_tool("add_axiom", {
                "owl_file_path": temp_owl_file,
                "axiom_str": "ClassAssertion(ex:Dog ex:Fido)"
            })
            
            # Query the ontology
            all_axioms = await session.invoke_tool("get_all_axioms", {
                "owl_file_path": temp_owl_file
            })
            
            print("All axioms in the ontology:")
            for axiom in all_axioms:
                print(f"  {axiom}")
            
            # Find specific axioms
            dog_axioms = await session.invoke_tool("find_axioms", {
                "owl_file_path": temp_owl_file,
                "pattern": "Dog"
            })
            
            print("\nAxioms related to 'Dog':")
            for axiom in dog_axioms:
                print(f"  {axiom}")
                
            # Get active OWL files
            active_files = await session.invoke_tool("list_active_owl_files", {})
            print(f"\nActive OWL files: {active_files}")

# Run the async function
asyncio.run(owl_example())
```

## Using OWL Server with AI Assistants

OWL Server can be used with AI assistants that support MCP integration. Here's an example of integrating with an LLM framework:

```python
import asyncio
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client
from langchain.llms import BaseLLM  # Example LLM framework
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType

async def owl_with_llm():
    # Configure the OWL MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "owl_mcp.mcp_tools"]
    )
    
    # Connect to the server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Create MCP tool wrappers for the LLM
            owl_tools = [
                Tool(
                    name="AddAxiom",
                    func=lambda args: asyncio.run(session.invoke_tool("add_axiom", {
                        "owl_file_path": args["file_path"],
                        "axiom_str": args["axiom"]
                    })),
                    description="Add an axiom to an OWL ontology. Args: file_path, axiom"
                ),
                Tool(
                    name="FindAxioms",
                    func=lambda args: asyncio.run(session.invoke_tool("find_axioms", {
                        "owl_file_path": args["file_path"],
                        "pattern": args["pattern"]
                    })),
                    description="Find axioms in an OWL ontology. Args: file_path, pattern"
                )
            ]
            
            # Initialize LLM and agent (placeholder - use your actual LLM)
            llm = BaseLLM()  # Replace with your actual LLM
            agent = initialize_agent(
                owl_tools, 
                llm, 
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True
            )
            
            # Example agent query
            result = agent.run(
                "Add the axiom 'SubClassOf(ex:Cat ex:Animal)' to my ontology at /path/to/ontology.owl"
            )
            print(result)

# This example requires actual LLM integration to run
# asyncio.run(owl_with_llm())
```

## Using OWL Server with Claude or GPT

AI assistants like Claude or GPT that have MCP capabilities can use OWL Server directly:

```
# Example prompt for Claude with MCP capabilities:

Use the OWL Server MCP tools to create a small ontology about pets.
Start by creating a file called "pets.owl" and add the following:
1. Standard OWL prefixes
2. Animal, Dog, Cat, and Bird classes
3. Make Dog, Cat, and Bird subclasses of Animal
4. Add some individual pets (e.g., "Fido" as a Dog)
5. Show me all the axioms in the ontology

# Claude would then use its MCP tools to execute these operations on the OWL Server
```

## Error Handling

When working with the MCP client, it's important to handle errors properly:

```python
import asyncio
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client
from mcp.errors import MCPToolError

async def error_handling_example():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "owl_mcp.mcp_tools"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            try:
                # Try to perform an operation on a non-existent file
                result = await session.invoke_tool("find_axioms", {
                    "owl_file_path": "/nonexistent/file.owl",
                    "pattern": "Dog"
                })
            except MCPToolError as e:
                print(f"MCP Tool Error: {e}")
            
            try:
                # Try to add an invalid axiom
                result = await session.invoke_tool("add_axiom", {
                    "owl_file_path": "example.owl",
                    "axiom_str": "Invalid Axiom Syntax"
                })
            except MCPToolError as e:
                print(f"MCP Tool Error: {e}")

# Run the async function
asyncio.run(error_handling_example())
```

## Running Multiple Operations Efficiently

To optimize performance, you can run multiple operations concurrently using `asyncio.gather`:

```python
import asyncio
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client

async def concurrent_operations():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "owl_mcp.mcp_tools"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Create a file path
            ontology_path = "animals.owl"
            
            # Run multiple operations concurrently
            results = await asyncio.gather(
                session.invoke_tool("add_axiom", {
                    "owl_file_path": ontology_path,
                    "axiom_str": "Declaration(Class(ex:Animal))"
                }),
                session.invoke_tool("add_axiom", {
                    "owl_file_path": ontology_path,
                    "axiom_str": "Declaration(Class(ex:Dog))"
                }),
                session.invoke_tool("add_axiom", {
                    "owl_file_path": ontology_path,
                    "axiom_str": "SubClassOf(ex:Dog ex:Animal))"
                })
            )
            
            for i, result in enumerate(results):
                print(f"Operation {i+1} result: {result}")
            
            # Get all axioms to verify
            axioms = await session.invoke_tool("get_all_axioms", {
                "owl_file_path": ontology_path
            })
            
            print("\nAll axioms:")
            for axiom in axioms:
                print(f"  {axiom}")

# Run the async function
asyncio.run(concurrent_operations())
```

## Next Steps

- Check the [API Reference](api-reference.md) for a complete list of available MCP tools
- See the [Architecture](../development/architecture.md) page to learn more about how OWL Server works
- Explore the [Contributing Guide](../development/contributing.md) if you want to help improve OWL Server