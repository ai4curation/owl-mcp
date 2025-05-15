import shutil

import pytest
from pyhornedowl.model import OntologyAnnotation

from owl_mcp.owl_api import SimpleOwlAPI
from tests import INPUT_DIR, OUTPUT_DIR


@pytest.fixture
def owl_api():
    shutil.copy(INPUT_DIR / "ro.owl", OUTPUT_DIR / "ro.owl")

    # Initialize API
    api = SimpleOwlAPI(str(OUTPUT_DIR / "ro.owl"))
    api.add_prefix("RO", "http://purl.obolibrary.org/obo/RO_")

    # Create closure for tracking events
    events = []

    def on_event(event_type, **kwargs):
        events.append((event_type, kwargs))

    api.add_observer(on_event)

    # Add events to api instance for test access
    api.test_events = events

    yield api

    # Cleanup
    api.stop()

def test_ontology_metadata(owl_api):
    """Test fetching ontology metadata."""
    assert len(owl_api.ontology_annotations()) > 3
    for a in owl_api.ontology_annotations():
        print(a)
    assert 'Annotation(<http://purl.org/dc/terms/title> "OBO Relations Ontology"@en)' in owl_api.get_all_axiom_strings()
    assert 'Annotation(<http://purl.org/dc/terms/title> "OBO Relations Ontology"@en)' in owl_api.ontology_annotations()

def test_api(owl_api):
    """Test adding an axiom."""
    axiom = "SubObjectPropertyOf(RO:1 RO:2)"
    owl_api.add_axiom(axiom)

    # Verify axiom was added to in-memory representation
    axioms = owl_api.get_all_axiom_strings()
    assert axiom in axioms

    owl_api.remove_axiom(axiom)
    axioms = owl_api.get_all_axiom_strings()
    assert axiom not in axioms
