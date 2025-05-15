# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OWL-Server is a Python server for managing OWL (Web Ontology Language) ontologies. It provides a simplified API for common operations like adding/removing axioms, finding axioms by pattern, and managing prefix mappings.

The project uses:
- py-horned-owl for OWL ontology manipulation
- watchdog for file monitoring
- click for command-line interface
- FastMCP for Model-Context-Protocol integration

## Architecture

The codebase is organized into these main components:

1. **SimpleOwlAPI** (`owl_api.py`): Core class that provides thread-safe ontology management:
   - Handles file synchronization with disk
   - Provides observer pattern for change notifications
   - Manages prefix mappings
   - Supports adding/removing/finding axioms
   - Respects readonly settings from configuration

2. **Axiom Parser** (`axiom_parser.py`): Handles conversion between string representations of OWL axioms and py-horned-owl objects.

3. **Server CLI** (`server.py`): Command-line interface for starting the server and initializing ontology files.

4. **MCP Tools** (`mcp_tools.py`): ModelContextProtocol wrapper around the core API:
   - Provides MCP tools for OWL operations
   - Handles API instance caching and management
   - Exposes file-path based interfaces for OWL manipulation
   - Includes configuration management tools

5. **Configuration System** (`config.py`): Manages session-wide configuration:
   - Stores ontology paths, metadata, and settings in `~/.owl-mcp/config.yaml`
   - Provides named access to frequently used ontologies
   - Supports readonly ontologies and metadata axioms
   - Offers session-wide settings like default serialization format

## Common Commands

### Installation

```bash
# Install dependencies and set up development environment
make install
```

### Running Tests

```bash
# Run all tests
make test

# Run a specific test
uv run pytest tests/test_owl_api.py::test_add_axiom

# Run tests with verbose output
uv run pytest -v

# Run only MCP tool tests
uv run pytest tests/test_mcp_tools.py
```

### Development Workflow

```bash
# Clean up build artifacts
make clean

# Run example script
make example
```

### Code Quality

```bash
# Format code with black
uv run black src tests

# Sort imports
uv run isort src tests

# Type checking with mypy
uv run mypy src
```

### Running the MCP Server

```bash
# Run the MCP server with stdio transport
python -m owl_server.mcp_tools
```

## Known Issues

The project has compatibility issues with py-horned-owl API as documented in KNOWN_ISSUES.md:

1. Methods like `add_default_prefix_names()` and `clazz()` are referenced in the code but may not be available in the installed version of py-horned-owl.
2. Adaptations may be needed for axiom types (SubClassOf, etc.).