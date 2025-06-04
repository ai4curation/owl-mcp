"""
Utilities for reading OASIS XML catalogs as commonly used in OWL ontologies.

This module provides a simple interface to parse XML catalog files and extract
IRI-to-file-path mappings for ontology import resolution.
"""

import os
import xml.etree.ElementTree as ET
from typing import Optional


def read_catalog(catalog_path: str, base_path: Optional[str] = None) -> dict[str, str]:
    """
    Read an OASIS XML catalog file and return IRI-to-file-path mappings.

    Args:
        catalog_path: Path to the XML catalog file
        base_path: Optional base directory for resolving relative paths.
                  If None, uses the directory containing the catalog file.

    Returns:
        Dictionary mapping IRIs (name attribute) to file paths (uri attribute)

    Raises:
        FileNotFoundError: If catalog file doesn't exist
        ET.ParseError: If catalog file is not valid XML
    """
    if not os.path.exists(catalog_path):
        raise FileNotFoundError(f"Catalog file not found: {catalog_path}")

    # Use catalog directory as base path if not specified
    if base_path is None:
        base_path = os.path.dirname(os.path.abspath(catalog_path))

    mappings = {}

    try:
        tree = ET.parse(catalog_path)
        root = tree.getroot()

        # Find all uri elements - namespace-aware search
        # Handle both with and without namespace prefix
        uri_elements = []

        # Try with namespace
        uri_elements.extend(root.findall(".//{urn:oasis:names:tc:entity:xmlns:xml:catalog}uri"))

        # Try without namespace (in case namespace is not properly declared)
        if not uri_elements:
            uri_elements.extend(root.findall(".//uri"))

        for uri_elem in uri_elements:
            name = uri_elem.get("name")
            uri_path = uri_elem.get("uri")

            if name and uri_path:
                # Resolve relative paths
                if not os.path.isabs(uri_path):
                    full_path = os.path.join(base_path, uri_path)
                    # Normalize the path
                    full_path = os.path.normpath(full_path)
                else:
                    full_path = uri_path

                mappings[name] = full_path

    except ET.ParseError as e:
        raise ET.ParseError(f"Error parsing catalog file {catalog_path}: {e}") from e

    return mappings


def find_catalog_file(directory: str, catalog_names: Optional[list] = None) -> Optional[str]:
    """
    Find a catalog file in the given directory.

    Args:
        directory: Directory to search for catalog file
        catalog_names: List of catalog filenames to look for.
                      Defaults to common catalog names.

    Returns:
        Path to catalog file if found, None otherwise
    """
    if catalog_names is None:
        catalog_names = ["catalog.xml", "catalog-v001.xml", "catalog-v1.xml"]

    for catalog_name in catalog_names:
        catalog_path = os.path.join(directory, catalog_name)
        if os.path.exists(catalog_path):
            return catalog_path

    return None


def resolve_iri(iri: str, catalog_mappings: dict[str, str]) -> Optional[str]:
    """
    Resolve an IRI to a file path using catalog mappings.

    Args:
        iri: The IRI to resolve
        catalog_mappings: Dictionary from read_catalog()

    Returns:
        File path if IRI is found in mappings, None otherwise
    """
    return catalog_mappings.get(iri)


def load_catalog_for_ontology(ontology_path: str) -> dict[str, str]:
    """
    Load catalog mappings for an ontology by looking for catalog files
    in the same directory as the ontology.

    Args:
        ontology_path: Path to the ontology file

    Returns:
        Dictionary of IRI-to-file-path mappings, empty if no catalog found
    """
    ontology_dir = os.path.dirname(os.path.abspath(ontology_path))
    catalog_path = find_catalog_file(ontology_dir)

    if catalog_path:
        return read_catalog(catalog_path, ontology_dir)

    return {}
