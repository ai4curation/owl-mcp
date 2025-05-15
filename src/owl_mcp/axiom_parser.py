import logging
import re
from typing import Optional

import pyhornedowl
from pyhornedowl import PyIndexedOntology
from pyhornedowl.model import AnnotatedComponent

logger = logging.getLogger("owl-server.parser")


def serialize_axioms(axioms: list[AnnotatedComponent], ontology: PyIndexedOntology) -> list[str]:
    """
    Serialize a list of OWL axioms into a string representation.

    Args:
        axioms: List of OWL axioms to serialize
        ontology: Optional ontology to use for prefix mappings

    Returns:
        String representation of the serialized axioms
    """
    temp_ontology = pyhornedowl.PyIndexedOntology()
    for prefix, url in ontology.prefix_mapping:
        temp_ontology.prefix_mapping.add_prefix(prefix, url)
    for axiom in axioms:
        temp_ontology.add_component(axiom.component, axiom.ann)
    ofn_str = temp_ontology.save_to_string("ofn").strip()
    # extract everything between Ontology( and final )
    re_pattern = r"Ontology\((.*?)\)$"
    match = re.search(re_pattern, ofn_str, re.DOTALL)
    if not match:
        error_msg = "Failed to extract ontology string from serialized OFN"
        raise ValueError(error_msg)
    ofn_str = match.group(1)
    lines = ofn_str.splitlines()
    return [line.strip() for line in lines if line.strip()]


def parse_axiom_string(
    axiom_str: str,
    ontology: Optional[PyIndexedOntology] = None,
    prefix_map: Optional[dict[str, str]] = None,
) -> list[AnnotatedComponent]:
    """
    Parse an OWL functional syntax string into an axiom.

    Args:
        axiom_str: String representation of the axiom in OWL functional syntax
        ontology: Optional ontology to use for prefix mappings
        prefix_map: Optional dictionary of prefix mappings

    Returns:
        The parsed axiom or None if parsing failed
    """
    # Build prefix declarations
    prefix_lines = []
    if ontology:
        for prefix, url in ontology.prefix_mapping:
            prefix_lines.append(f"Prefix( {prefix}: = <{url}> )")
    if prefix_map:
        for prefix, url in prefix_map.items():
            prefix_lines.append(f"Prefix( {prefix}: = <{url}> )")

    # Create a single-axiom ontology string
    header = "\n".join(prefix_lines)
    owl_str = f"{header}\nOntology(<http://example.org>\n{axiom_str}\n)"
    logger.debug(f"Parsing axiom string:\n{owl_str}")

    # Parse the ontology and extract the axiom
    ont = pyhornedowl.open_ontology_from_string(owl_str, "ofn")
    return ont.get_axioms()
