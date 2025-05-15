import os
import tempfile

import pytest

from owl_mcp.owl_api import SimpleOwlAPI


@pytest.fixture
def owl_api_with_labels():
    """Fixture that provides a SimpleOwlAPI instance with annotation assertions."""
    # Create a temporary OWL file for testing
    with tempfile.NamedTemporaryFile(suffix=".ofn", delete=False) as temp_file:
        temp_file.write(b"""
    Prefix(ex:=<http://example.org/>)
    Prefix(rdfs:=<http://www.w3.org/2000/01/rdf-schema#>)
    Ontology(<http://example.org/test>)
    """)
        temp_file.close()

    # Initialize API
    api = SimpleOwlAPI(temp_file.name)
    
    # Add some classes with labels
    api.add_axiom("Declaration(Class(ex:Person))")
    api.add_axiom("Declaration(Class(ex:Animal))")
    api.add_axiom("Declaration(Class(ex:Dog))")
    
    # Add labels to these classes
    api.add_axiom("AnnotationAssertion(rdfs:label ex:Person \"Person\")")
    api.add_axiom("AnnotationAssertion(rdfs:label ex:Animal \"Animal\")")
    api.add_axiom("AnnotationAssertion(rdfs:label ex:Dog \"Dog\")")
    
    # Add a different annotation type
    api.add_axiom("AnnotationAssertion(ex:definition ex:Person \"A human being\")")
    
    # Add a class axiom to test with labels
    api.add_axiom("SubClassOf(ex:Dog ex:Animal)")

    api.temp_file_path = temp_file.name

    yield api

    # Cleanup
    api.stop()
    os.unlink(temp_file.name)


def test_get_labels_for_iri(owl_api_with_labels):
    """Test retrieving labels for an IRI."""
    # Test getting labels with default annotation property (rdfs:label)
    labels = owl_api_with_labels.get_labels_for_iri("ex:Person")
    assert len(labels) == 1
    assert "Person" in labels

    # Test getting labels with specified annotation property
    definitions = owl_api_with_labels.get_labels_for_iri("ex:Person", "http://example.org/definition")
    assert len(definitions) == 1
    assert "A human being" in definitions

    # Test getting labels for IRI without labels
    labels = owl_api_with_labels.get_labels_for_iri("ex:NonExistentClass")
    assert len(labels) == 0

    # Test getting labels with non-existent annotation property
    labels = owl_api_with_labels.get_labels_for_iri("ex:Person", "http://example.org/nonexistent")
    assert len(labels) == 0


def test_get_axioms_with_labels(owl_api_with_labels):
    """Test retrieving axioms with human-readable labels."""
    # Get all axioms without labels
    axioms = owl_api_with_labels.get_all_axiom_strings(include_labels=False)
    subclass_axiom = next(a for a in axioms if a.startswith("SubClassOf"))
    
    # Verify no labels are included
    assert "##" not in subclass_axiom
    
    # Get axioms with labels
    labeled_axioms = owl_api_with_labels.get_all_axiom_strings(include_labels=True)
    labeled_subclass_axiom = next(a for a in labeled_axioms if a.startswith("SubClassOf"))
    
    # Verify labels are included
    assert "##" in labeled_subclass_axiom
    assert "Dog" in labeled_subclass_axiom
    assert "Animal" in labeled_subclass_axiom
    assert 'SubClassOf(ex:Dog ex:Animal) ## ex:Dog = "Dog"; ex:Animal = "Animal"' == labeled_subclass_axiom


def test_find_axioms_with_labels(owl_api_with_labels):
    """Test finding axioms with human-readable labels."""
    # Find axioms without labels
    axioms = owl_api_with_labels.find_axioms("SubClassOf", include_labels=False)
    assert len(axioms) == 1
    assert "##" not in axioms[0]
    
    # Find axioms with labels
    labeled_axioms = owl_api_with_labels.find_axioms("SubClassOf", include_labels=True)
    assert len(labeled_axioms) == 1
    assert "##" in labeled_axioms[0]
    assert "Dog" in labeled_axioms[0]
    assert "Animal" in labeled_axioms[0]
    
    # Find with specific annotation property 
    custom_labeled_axioms = owl_api_with_labels.find_axioms(
        "SubClassOf", 
        include_labels=True,
        annotation_property="http://example.org/definition"
    )
    
    # Should include the axiom (which has Dog and Animal terms since they're part of the axiom)
    assert len(custom_labeled_axioms) == 1
    
    # Here we're checking if labels with "=" symbol are NOT included, 
    # since our custom property doesn't have values
    assert "=" not in custom_labeled_axioms[0]