# OWL-MCP

OWL-MCP is a Model-Context-Protocol (MCP) server for working with Web Ontology Language (OWL) ontologies. 

![img](https://avatars.githubusercontent.com/u/182288589?s=200&v=4)
![img](https://avatars.githubusercontent.com/u/4671070?s=200&v=4) 

## Quick Start

This walks you through using owl-mcp with [Goose](https://github.com/block/goose), but any MCP-enabled AI host will work.

### Install Goose

You can use either the Desktop or CLI version of Goose from here:

* [goose installation](https://block.github.io/goose/docs/getting-started/installation/)

Follow the instructions for setting up an LLM provider (Anthropic recommended)

### Install OWL-MCP extension

You can either install directly from this link:

 * [Install OWL-MCP](goose://extension?cmd=uvx&arg=owl-mcp&id=owl_mcp&name=OWL%20MCP)

 Or to do this manually, in the Extension section of Goose, add a new entry for owlmcp:

 `uvx owl-mcp`

 This video shows how to do this manually:

<iframe 
  width="500" 
  height="560" 
  src="https://www.youtube.com/embed/509qVPEbv0Q" 
  title="YouTube video player" 
  frameborder="0" 
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
  allowfullscreen>
</iframe>
 
### Try it out

You can ask to create an ontology, and add axioms to an ontology:

<iframe 
  width="500" 
  height="560" 
  src="https://www.youtube.com/embed/sAXs3djX854" 
  title="YouTube video player" 
  frameborder="0" 
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
  allowfullscreen>
</iframe>
 

## How this works

The MCP server provides function calls for finding, adding, or removing OWL axioms, using OWL functional syntax. Each function call is accompanied by the file path of the OWL file on your disk. Any format supported by py-horned-owl is accepted (we following OBO guidelines and recommend functional syntax for source).

The server takes care of keeping an instance of the ontology in memory and syncing it with disk. Any CRUD operation simultaneously updates the in-memory model and syncs this with disk. If you have Protege running, Protege will also
sync with local disk, and show updates.

The server is well adapted for working with OBO-style ontologies - when OWL strings are sent back to the client, labels for opaque IDs are included after `#`s comments, as is common for obo-format.

## Key Features

- **MCP Server Integration**: Connect AI assistants directly to OWL ontologies using the standardized Model-Context-Protocol
- **Thread-safe operations**: All ontology operations are thread-safe, making it suitable for multi-user environments
- **File synchronization**: Changes to the ontology file on disk are automatically detected and synchronized
- **Event-based notifications**: Register observers to be notified of changes to the ontology
- **Simple string-based API**: Work with OWL axioms as strings in functional syntax without dealing with complex object models
- **Configuration system**: Store and manage settings for frequently-used ontologies
- **Label support**: Access human-readable labels for entities with configurable annotation properties

