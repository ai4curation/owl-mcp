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

## What are the requirements for this tool?

You will need an API key to access an LLM. We recommend Claude/Anthropic but you can try others.

We also recommend having some kind of standard coding environment set up. For Macs, this involves installing xcode. The AI can walk you through this.

## How do I use this?

There are a lot of applications that support MCP

* [goose](https://block.github.io/goose)
* [Claude Desktop](https://claude.ai/download)
* Most IDEs

Once you are in your app, you can configure it to use owl-mcp by providing details on how to start the server:

```
uvx owl-mcp
```

Once you have done this, you can ask the AI to create a new ontology, or to work with an existing ontology which you have locally.

You can do pretty much anything through the chat interface of the AI tool, try this:

* ask the AI to create a new ontology in a folder of your choosing
* ask the AI to clone an existing ontology repo. You can give a URL but it will likely be able to find repos, especially for well known OBO ontologies like the cell ontology.