"""
MCP tools for working with OWL ontologies.

This module provides a Model-Context-Protocol wrapper around
the OWL Server functionality, allowing integration with other MCP systems.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from pyhornedowl.model import OntologyAnnotation

from owl_mcp.axiom_parser import serialize_axioms
from owl_mcp.config import OntologyConfig, get_config_manager, OWLMCPConfig
from owl_mcp.owl_api import SimpleOwlAPI

# Initialize FastMCP server
mcp = FastMCP(
    "owl-server",
    instructions="""
OWL Server provides tools for managing Web Ontology Language (OWL) ontologies.
Use these tools to add, remove, and find axioms in OWL files, and to manage prefix mappings.

The tools operate on OWL files specified either by:
1. Absolute file paths (e.g., /path/to/ontology.owl)
2. Named ontologies from the configuration (e.g., "my-ontology")

## Configuration System

OWL-Server includes a configuration system that stores ontology metadata and settings 
in ~/.owl-mcp/config.yaml. This allows you to:

- Define named ontologies with paths and metadata
- Set ontologies as readonly to prevent modifications
- Add default metadata axioms to ontologies
- Specify preferred serialization formats

To work with configured ontologies, use the configuration tools or the "by_name" variants
of the standard tools.

## Resources

The server provides the following resources:
- `resource://config/ontologies` - List of all configured ontologies
- `resource://config/ontology/{name}` - Details about a specific ontology configuration
- `resource://active` - List of all active OWL file paths
""",
)


@mcp.prompt()
def ask_for_axioms_about(topic: str) -> str:
    """Generates a user message asking for axioms matching a string."""
    return f"What axioms include the string '{topic}'?"


# Dictionary to cache SimpleOwlAPI instances
_api_instances = {}


def _get_api_instance(owl_file_path: str, auto_register: bool = False) -> SimpleOwlAPI:
    """
    Get or create a SimpleOwlAPI instance for the given file path.

    Args:
        owl_file_path: Absolute path to the OWL file
        auto_register: If True and the ontology is not in the configuration yet,
                      automatically register it

    Returns:
        SimpleOwlAPI: Instance for the given file path
    """
    owl_file_path = os.path.abspath(owl_file_path)

    if owl_file_path not in _api_instances:
        # Check if we have configuration for this file
        config_manager = get_config_manager()
        ontology_config = config_manager.get_ontology_by_path(owl_file_path)
        
        if ontology_config:
            # Use configured settings
            _api_instances[owl_file_path] = SimpleOwlAPI(
                owl_file_path,
                serialization=ontology_config.preferred_serialization,
                readonly=ontology_config.readonly,
                annotation_property=ontology_config.annotation_property
            )
        else:
            # Use default settings
            _api_instances[owl_file_path] = SimpleOwlAPI(owl_file_path)
            
            # Auto-register if requested
            if auto_register:
                _api_instances[owl_file_path].register_in_config()

    return _api_instances[owl_file_path]


@mcp.tool()
async def add_axiom(owl_file_path: str, axiom_str: str) -> str:
    """
    Add an axiom to the ontology using OWL functional syntax.

    Args:
        owl_file_path: Absolute path to the OWL file
        axiom_str: String representation of the axiom in OWL functional syntax
                 e.g., "SubClassOf(:Dog :Animal)"

    Returns:
        str: Success message or error
    """
    api = _get_api_instance(owl_file_path)
    success = api.add_axiom(axiom_str)

    if success:
        return f"Successfully added axiom: {axiom_str}"
    return f"Failed to add axiom: {axiom_str}"


@mcp.tool()
async def remove_axiom(owl_file_path: str, axiom_str: str) -> str:
    """
    Remove an axiom from the ontology using OWL functional syntax.

    Args:
        owl_file_path: Absolute path to the OWL file
        axiom_str: String representation of the axiom in OWL functional syntax

    Returns:
        str: Success message or error
    """
    api = _get_api_instance(owl_file_path)
    success = api.remove_axiom(axiom_str)

    if success:
        return f"Successfully removed axiom: {axiom_str}"
    return f"Failed to remove axiom: {axiom_str}"


@mcp.tool()
async def find_axioms(
    owl_file_path: str, 
    pattern: str, 
    limit=100, 
    include_labels: bool = False,
    annotation_property: Optional[str] = None
) -> list[str]:
    """
    Find axioms matching a pattern in the ontology.

    Args:
        owl_file_path: Absolute path to the OWL file
        pattern: A string pattern to match against axiom strings
                (simple substring matching)
        limit: Maximum number of axioms to return (default: 100)
        include_labels: If True, include human-readable labels after ## in the output
        annotation_property: Optional annotation property IRI to use for labels 
                            (defaults to rdfs:label)

    Returns:
        list[str]: List of matching axiom strings
    """
    api = _get_api_instance(owl_file_path)
    return api.find_axioms(pattern, 
                         include_labels=include_labels, 
                         annotation_property=annotation_property)[0:limit]


@mcp.tool()
async def get_all_axioms(
    owl_file_path: str, 
    limit=100, 
    include_labels: bool = False,
    annotation_property: Optional[str] = None
) -> list[str]:
    """
    Get all axioms in the ontology as strings.

    Args:
        owl_file_path: Absolute path to the OWL file
        limit: Maximum number of axioms to return (default: 100)
        include_labels: If True, include human-readable labels after ## in the output
        annotation_property: Optional annotation property IRI to use for labels 
                            (defaults to rdfs:label)

    Returns:
        list[str]: List of all axiom strings
    """
    api = _get_api_instance(owl_file_path)
    return api.get_all_axiom_strings(
        include_labels=include_labels, 
        annotation_property=annotation_property
    )[0:limit]


@mcp.tool()
async def add_prefix(owl_file_path: str, prefix: str, uri: str) -> str:
    """
    Add a prefix mapping to the ontology.

    Args:
        owl_file_path: Absolute path to the OWL file
        prefix: The prefix string (e.g., "ex:")
        uri: The URI the prefix maps to (e.g., "http://example.org/")

    Returns:
        str: Success message
    """
    api = _get_api_instance(owl_file_path)
    success = api.add_prefix(prefix, uri)

    if success:
        return f"Successfully added prefix mapping: {prefix} -> {uri}"
    return f"Failed to add prefix mapping: {prefix} -> {uri}"


@mcp.tool()
async def ontology_metadata(owl_file_path: str) -> list[str]:
    """
    Get metadata about the ontology.

    Args:
        owl_file_path: Absolute path to the OWL file

    Returns:
        list[str]: List of metadata items
    """
    api = _get_api_instance(owl_file_path)
    return api.ontology_annotations()


# Configuration resources

@mcp.resource("resource://config/ontologies")
async def get_config_ontologies() -> OWLMCPConfig:
    """
    Resource that provides a list of all configured ontologies.

    Returns:
        List[OntologyConfigInfo]: List of configured ontologies with their details
    """
    config_manager = get_config_manager()
    return config_manager.config



@mcp.resource("resource://active")
async def list_active_owl_files() -> list[str]:
    """
    List all OWL files currently being managed.

    Returns:
        list[str]: List of file paths for active OWL files
    """
    return list(_api_instances.keys())


async def stop_owl_service(owl_file_path: str) -> str:
    owl_file_path = os.path.abspath(owl_file_path)
    api = _api_instances.get(owl_file_path)
    if api:
        api.stop()
        del _api_instances[owl_file_path]
        return f"Successfully stopped OWL service for {owl_file_path}"
    return "No OWL service running for this file"


# Configuration tools

class OntologyConfigInfo(BaseModel):
    """Simplified model for OntologyConfig that can be passed through MCP."""
    name: str
    path: str
    metadata_axioms: List[str]
    readonly: bool
    description: Optional[str] = None
    preferred_serialization: Optional[str] = None
    annotation_property: Optional[str] = None


@mcp.tool()
async def list_configured_ontologies() -> List[OntologyConfigInfo]:
    """
    List all ontologies defined in the configuration.
    
    Returns:
        List[OntologyConfigInfo]: List of configured ontologies
    """
    config_manager = get_config_manager()
    ontologies = config_manager.list_ontologies()
    
    result = []
    for name, config in ontologies.items():
        result.append(OntologyConfigInfo(
            name=name,
            path=config.path,
            metadata_axioms=config.metadata_axioms,
            readonly=config.readonly,
            description=config.description,
            preferred_serialization=config.preferred_serialization,
            annotation_property=config.annotation_property
        ))
    
    return result


@mcp.tool()
async def configure_ontology(
    name: str,
    path: str,
    metadata_axioms: Optional[List[str]] = None,
    readonly: bool = False,
    description: Optional[str] = None,
    preferred_serialization: Optional[str] = None,
    annotation_property: Optional[str] = None
) -> str:
    """
    Add or update an ontology in the configuration.
    
    Args:
        name: A unique name for the ontology
        path: Absolute path to the ontology file
        metadata_axioms: List of metadata axioms as strings
        readonly: Whether the ontology is read-only (default: False)
        description: Optional description
        preferred_serialization: Optional preferred serialization format
        annotation_property: Optional annotation property IRI for labels (default: rdfs:label)
    
    Returns:
        str: Success or error message
    """
    config_manager = get_config_manager()
    
    # Check if the ontology is already loaded
    path = os.path.abspath(path)
    if path in _api_instances:
        # Reload with new settings
        api = _api_instances[path]
        api.stop()
        del _api_instances[path]
    
    # Add to configuration
    config_manager.add_ontology(
        name=name,
        path=path,
        metadata_axioms=metadata_axioms or [],
        readonly=readonly,
        description=description,
        preferred_serialization=preferred_serialization,
        annotation_property=annotation_property
    )
    
    # Try to verify the file exists
    if not os.path.exists(path):
        return f"Configured ontology '{name}' at {path}, but file does not exist yet."
    
    return f"Successfully configured ontology '{name}' at {path}"


@mcp.tool()
async def remove_ontology_config(name: str) -> str:
    """
    Remove an ontology from the configuration.
    
    Args:
        name: Name of the ontology to remove
    
    Returns:
        str: Success or error message
    """
    config_manager = get_config_manager()
    ontology_config = config_manager.get_ontology(name)
    
    if not ontology_config:
        return f"No ontology with name '{name}' found in configuration."
    
    # Check if the ontology is currently loaded
    path = os.path.abspath(ontology_config.path)
    if path in _api_instances:
        # Stop the service
        await stop_owl_service(path)
    
    # Remove from configuration
    config_manager.remove_ontology(name)
    return f"Successfully removed ontology '{name}' from configuration."


@mcp.tool()
async def get_ontology_config(name: str) -> Optional[OntologyConfigInfo]:
    """
    Get configuration for a specific ontology.
    
    Args:
        name: Name of the ontology
    
    Returns:
        Optional[OntologyConfigInfo]: The ontology configuration or None if not found
    """
    config_manager = get_config_manager()
    config = config_manager.get_ontology(name)
    
    if not config:
        return None
        
    return OntologyConfigInfo(
        name=name,
        path=config.path,
        metadata_axioms=config.metadata_axioms,
        readonly=config.readonly,
        description=config.description,
        preferred_serialization=config.preferred_serialization,
        annotation_property=config.annotation_property
    )


@mcp.tool()
async def register_ontology_in_config(
    owl_file_path: str,
    name: Optional[str] = None,
    readonly: Optional[bool] = None,
    description: Optional[str] = None,
    preferred_serialization: Optional[str] = None,
    annotation_property: Optional[str] = None
) -> str:
    """
    Register an existing ontology in the configuration system.
    
    This allows you to save preferences and metadata for frequently used ontologies,
    making them accessible by name in future sessions.
    
    Args:
        owl_file_path: Absolute path to the ontology file
        name: Optional custom name for the ontology (defaults to filename without extension)
        readonly: Whether the ontology should be read-only (defaults to current setting if loaded)
        description: Optional description for the ontology
        preferred_serialization: Optional preferred serialization format
        annotation_property: Optional annotation property IRI for labels (defaults to current setting if loaded)
    
    Returns:
        str: Name of the registered ontology
    """
    # Get or create the API instance
    api = _get_api_instance(owl_file_path)
    
    # Register in configuration
    registered_name = api.register_in_config(
        name=name,
        readonly=readonly,
        description=description,
        preferred_serialization=preferred_serialization,
        annotation_property=annotation_property
    )
    
    return f"Successfully registered ontology '{registered_name}' in configuration"


@mcp.tool()
async def load_and_register_ontology(
    owl_file_path: str,
    name: Optional[str] = None,
    readonly: bool = False,
    create_if_not_exists: bool = True,
    description: Optional[str] = None,
    preferred_serialization: Optional[str] = None,
    metadata_axioms: Optional[List[str]] = None,
    annotation_property: Optional[str] = None
) -> str:
    """
    Load an ontology and register it in the configuration system in one step.
    
    Args:
        owl_file_path: Absolute path to the ontology file
        name: Optional name for the ontology (defaults to filename stem)
        readonly: Whether the ontology should be read-only (default: False)
        create_if_not_exists: If True, create the file if it doesn't exist (default: True)
        description: Optional description of the ontology
        preferred_serialization: Optional preferred serialization format
        metadata_axioms: Optional list of metadata axioms to add to the ontology
        annotation_property: Optional annotation property IRI for labels (default: rdfs:label)
        
    Returns:
        str: Success message
    """
    # Convert to absolute path
    owl_file_path = os.path.abspath(owl_file_path)
    
    # Check if the ontology is already registered
    config_manager = get_config_manager()
    
    # If name is not provided, derive it from the filename
    if name is None:
        name = Path(owl_file_path).stem
    
    # Check if we need to create the file
    file_exists = os.path.exists(owl_file_path)
    if not file_exists and not create_if_not_exists:
        return f"File does not exist: {owl_file_path}"
    
    # Get or create an API instance (don't auto-register yet)
    api = _get_api_instance(owl_file_path)
    
    # Add metadata axioms if provided
    if metadata_axioms:
        for axiom in metadata_axioms:
            api.add_axiom(axiom, bypass_readonly=True)
    
    # Register in configuration
    api.register_in_config(
        name=name,
        readonly=readonly,
        description=description,
        preferred_serialization=preferred_serialization,
        annotation_property=annotation_property
    )
    
    # Determine if the file was created or opened
    action = "Created and registered" if not file_exists else "Loaded and registered"
    
    return f"{action} ontology '{name}' at {owl_file_path}"


# Tools to work with configured ontologies by name

def _get_ontology_path_by_name(name: str) -> Optional[str]:
    """
    Helper function to get the path for a configured ontology by name.
    
    Args:
        name: Name of the ontology in the configuration
        
    Returns:
        Optional[str]: Path to the ontology file or None if not found
    """
    config_manager = get_config_manager()
    config = config_manager.get_ontology(name)
    
    if not config:
        return None
        
    return config.path


@mcp.tool()
async def add_axiom_by_name(ontology_name: str, axiom_str: str) -> str:
    """
    Add an axiom to a configured ontology using its name.
    
    Args:
        ontology_name: Name of the ontology as defined in configuration
        axiom_str: String representation of the axiom in OWL functional syntax
    
    Returns:
        str: Success message or error
    """
    owl_file_path = _get_ontology_path_by_name(ontology_name)
    if not owl_file_path:
        return f"No ontology with name '{ontology_name}' found in configuration."
        
    return await add_axiom(owl_file_path, axiom_str)


@mcp.tool()
async def remove_axiom_by_name(ontology_name: str, axiom_str: str) -> str:
    """
    Remove an axiom from a configured ontology using its name.
    
    Args:
        ontology_name: Name of the ontology as defined in configuration
        axiom_str: String representation of the axiom in OWL functional syntax
    
    Returns:
        str: Success message or error
    """
    owl_file_path = _get_ontology_path_by_name(ontology_name)
    if not owl_file_path:
        return f"No ontology with name '{ontology_name}' found in configuration."
        
    return await remove_axiom(owl_file_path, axiom_str)


@mcp.tool()
async def find_axioms_by_name(
    ontology_name: str, 
    pattern: str, 
    limit=100, 
    include_labels: bool = False,
    annotation_property: Optional[str] = None
) -> list[str]:
    """
    Find axioms matching a pattern in a configured ontology using its name.
    
    Args:
        ontology_name: Name of the ontology as defined in configuration
        pattern: A string pattern to match against axiom strings
        limit: Maximum number of axioms to return (default: 100)
        include_labels: If True, include human-readable labels after ## in the output
        annotation_property: Optional annotation property IRI to use for labels 
                            (defaults to rdfs:label)
    
    Returns:
        list[str]: List of matching axiom strings or empty list if ontology not found
    """
    owl_file_path = _get_ontology_path_by_name(ontology_name)
    if not owl_file_path:
        return []
        
    return await find_axioms(
        owl_file_path, 
        pattern, 
        limit, 
        include_labels=include_labels,
        annotation_property=annotation_property
    )


@mcp.tool()
async def add_prefix_by_name(ontology_name: str, prefix: str, uri: str) -> str:
    """
    Add a prefix mapping to a configured ontology using its name.
    
    Args:
        ontology_name: Name of the ontology as defined in configuration
        prefix: The prefix string (e.g., "ex:")
        uri: The URI the prefix maps to (e.g., "http://example.org/")
    
    Returns:
        str: Success message or error
    """
    owl_file_path = _get_ontology_path_by_name(ontology_name)
    if not owl_file_path:
        return f"No ontology with name '{ontology_name}' found in configuration."
        
    return await add_prefix(owl_file_path, prefix, uri)


@mcp.tool()
async def get_labels_for_iri(
    owl_file_path: str, 
    iri: str, 
    annotation_property: Optional[str] = None
) -> List[str]:
    """
    Get all labels for a given IRI.
    
    Args:
        owl_file_path: Absolute path to the OWL file
        iri: The IRI to get labels for (as a string)
        annotation_property: Optional annotation property IRI to use for labels
                            (defaults to rdfs:label if None)
    
    Returns:
        List[str]: List of label strings
    """
    api = _get_api_instance(owl_file_path)
    return api.get_labels_for_iri(iri, annotation_property)


@mcp.tool()
async def get_labels_for_iri_by_name(
    ontology_name: str, 
    iri: str, 
    annotation_property: Optional[str] = None
) -> List[str]:
    """
    Get all labels for a given IRI in a configured ontology.
    
    Args:
        ontology_name: Name of the ontology as defined in configuration
        iri: The IRI to get labels for (as a string)
        annotation_property: Optional annotation property IRI to use for labels
                            (defaults to rdfs:label if None)
    
    Returns:
        List[str]: List of label strings or empty list if ontology not found
    """
    owl_file_path = _get_ontology_path_by_name(ontology_name)
    if not owl_file_path:
        return []
        
    return await get_labels_for_iri(owl_file_path, iri, annotation_property)


def main():
    """
    Run the MCP server.
    """
    mcp.run(transport="stdio")


if __name__ == "__main__":
    # Initialize and run the server
    main()
