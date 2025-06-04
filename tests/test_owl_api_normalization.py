import shutil

import pytest

from owl_mcp.owl_api import SimpleOwlAPI
from tests import INPUT_DIR, OUTPUT_DIR

EXPECTED_MIN_ONTOLOGY_ANNOTATIONS = 3

test_input_dir = INPUT_DIR / "normalize-test"
test_output_dir = OUTPUT_DIR / "normalize-test"


@pytest.fixture
def owl_api():
    # copy recursively from test_input_dir to test_output_dir, after first removing the test_output_dir
    if test_output_dir.exists():
        shutil.rmtree(test_output_dir)
    shutil.copytree(test_input_dir, test_output_dir)

    # Initialize API
    api = SimpleOwlAPI(str(test_output_dir / "ro.ofn"))

    # Create closure for tracking events
    events = []

    def on_event(event_type, **kwargs):
        events.append((event_type, kwargs))

    api.add_observer(on_event)

    # Add events to api instance for test access
    api.test_events = events

    assert not api.readonly

    yield api

    # Cleanup
    api.stop()


def test_ontology_metadata(owl_api):
    """Test fetching ontology metadata."""
    assert len(owl_api.ontology_annotations()) > EXPECTED_MIN_ONTOLOGY_ANNOTATIONS
    for a in owl_api.ontology_annotations():
        print(a)
    assert 'Annotation(terms:title "OBO Relations Ontology"@en)' in owl_api.get_all_axiom_strings()
    assert 'Annotation(terms:title "OBO Relations Ontology"@en)' in owl_api.ontology_annotations()


def test_api(owl_api):
    # check if `robot` is in the path, skip if not
    if not shutil.which("robot"):
        pytest.skip("robot is not in the path")

    """Test adding an axiom."""
    axiom = "SubObjectPropertyOf(obo:RO_1 obo:RO_2)"
    owl_api.add_axiom(axiom)

    # Verify axiom was added to in-memory representation
    axioms = owl_api.get_all_axiom_strings()
    assert axiom in axioms

    api_copy = SimpleOwlAPI(str(test_output_dir / "ro.ofn"))
    api_copy.add_prefix("RO", "http://purl.obolibrary.org/obo/RO_")
    axioms = api_copy.get_all_axiom_strings()
    assert axiom in axioms

    owl_api.remove_axiom(axiom)
    axioms = owl_api.get_all_axiom_strings()
    assert axiom not in axioms
