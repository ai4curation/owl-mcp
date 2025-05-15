import os
import tempfile

import pytest

from owl_mcp.owl_api import SimpleOwlAPI


@pytest.fixture
def owl_api():
    """Fixture that provides an initialized SimpleOwlAPI instance."""
    # Create a temporary OWL file for testing
    with tempfile.NamedTemporaryFile(suffix=".ofn", delete=False) as temp_file:
        temp_file.write(b"""
    Prefix(ex:=<http://example.org/>)
    Ontology(<http://example.org/test>)
    """)
        temp_file.close()

    # Initialize API
    api = SimpleOwlAPI(temp_file.name)

    # Create closure for tracking events
    events = []

    def on_event(event_type, **kwargs):
        events.append((event_type, kwargs))

    api.add_observer(on_event)

    # Add events to api instance for test access
    api.test_events = events
    api.temp_file_path = temp_file.name

    yield api

    # Cleanup
    api.stop()
    os.unlink(temp_file.name)


def test_add_axiom(owl_api):
    """Test adding an axiom."""
    axiom = "ClassAssertion(ex:Person ex:John)"

    # Store the file's original modification time
    original_mtime = os.path.getmtime(owl_api.temp_file_path)

    # Add the axiom
    success = owl_api.add_axiom(axiom)
    assert success is True

    # Check if event was fired
    assert len(owl_api.test_events) == 1
    event_type, event_data = owl_api.test_events[0]
    assert event_type == "axiom_added"
    assert event_data["axiom_str"] == axiom

    # Verify axiom was added to in-memory representation
    axioms = owl_api.get_all_axiom_strings()
    assert axiom in axioms

    # Check that the file was actually updated on disk
    current_mtime = os.path.getmtime(owl_api.temp_file_path)
    assert current_mtime > original_mtime, "File modification time should have changed"

    # Verify file content contains the added axiom
    with open(owl_api.temp_file_path) as f:
        file_content = f.read()
        assert ":Person" in file_content, "File should contain the added class"
        assert ":John" in file_content, "File should contain the added individual"


def test_remove_axiom(owl_api):
    """Test removing an axiom."""
    # First add an axiom
    axiom = "ClassAssertion(ex:Person ex:John)"
    owl_api.add_axiom(axiom)
    owl_api.test_events.clear()

    # Then remove it
    success = owl_api.remove_axiom(axiom)
    assert success is True

    # Check if event was fired
    assert len(owl_api.test_events) == 1
    event_type, event_data = owl_api.test_events[0]
    assert event_type == "axiom_removed"
    assert event_data["axiom_str"] == axiom

    # Verify axiom was removed
    axioms = owl_api.get_all_axiom_strings()
    assert axiom not in axioms


def test_find_axioms(owl_api):
    """Test finding axioms."""
    # Add some test axioms
    axioms = [
        "ClassAssertion(ex:Person ex:John)",
        "ClassAssertion(ex:Person ex:Jane)",
        "ObjectPropertyAssertion(ex:knows ex:John ex:Jane)",
    ]
    for axiom in axioms:
        owl_api.add_axiom(axiom)

    # Define expected counts for clarity
    num_class_assertions = 2
    num_john_mentions = 2
    num_john_class_assertions = 1

    # Test finding axioms by pattern
    found = owl_api.find_axioms("ClassAssertion")
    assert len(found) == num_class_assertions
    assert axioms[0] in found
    assert axioms[1] in found

    found = owl_api.find_axioms(":John")
    assert len(found) == num_john_mentions
    assert axioms[0] in found
    assert axioms[2] in found

    found = owl_api.find_axioms(":John", "ClassAssertion")
    assert len(found) == num_john_class_assertions
    assert axioms[0] in found

    found = owl_api.find_axioms("", "ClassAssertion")
    assert len(found) == num_class_assertions
    assert axioms[0] in found
    assert axioms[1] in found

    found = owl_api.find_axioms(None, "ClassAssertion")
    assert len(found) == num_class_assertions
    assert axioms[0] in found
    assert axioms[1] in found


def test_add_prefix(owl_api):
    """Test adding a prefix."""
    prefix = "test:"
    uri = "http://test.org/"
    owl_api.test_events.clear()
    success = owl_api.add_prefix(prefix, uri)
    assert success is True

    # Check if event was fired
    assert len(owl_api.test_events) == 1
    event_type, event_data = owl_api.test_events[0]
    assert event_type == "prefix_added"
    assert event_data["prefix"] == prefix
    assert event_data["uri"] == uri


def test_observer_management(owl_api):
    """Test observer management."""

    # Test adding observer
    def test_callback(event_type, **kwargs):
        pass

    owl_api.add_observer(test_callback)
    assert test_callback in owl_api.observers

    # Test removing observer
    owl_api.remove_observer(test_callback)
    assert test_callback not in owl_api.observers


def test_file_synchronization(owl_api):
    """Test file synchronization when file is modified externally."""
    # First add an axiom to ensure the file has content
    owl_api.add_axiom("ClassAssertion(ex:Person ex:Bob)")
    owl_api.test_events.clear()

    # Create a new API instance pointing to the same file to simulate external change
    external_api = SimpleOwlAPI(owl_api.temp_file_path)

    # Add an axiom through this separate API instance
    external_api.add_axiom("ClassAssertion(ex:Person ex:Alice)")

    # Clean up the external API
    external_api.stop()

    # Trigger sync (normally would happen via file watcher)
    owl_api.sync_with_file()

    # Verify the new axiom was detected
    axioms = owl_api.get_all_axiom_strings()
    bob_found = any(":Bob" in axiom for axiom in axioms)
    alice_found = any(":Alice" in axiom for axiom in axioms)

    assert bob_found, "Original axiom should still be present"
    assert alice_found, "Externally added axiom should be detected"

    # Verify event was fired
    assert len(owl_api.test_events) == 1
    event_type, _ = owl_api.test_events[0]
    assert event_type == "file_changed", "File changed event should be triggered"


def test_file_watchdog():
    """Test that the watchdog monitoring system is properly set up and detects file changes."""
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(suffix=".ofn", delete=False) as temp_file:
        temp_file.write(b"Ontology()")
        temp_file.close()

    try:
        # Initialize API
        api = SimpleOwlAPI(temp_file.name)

        # Verify the watchdog monitor is set up
        assert api.file_monitor is not None, "File monitor should be initialized"
        assert api.file_monitor.is_alive(), "File monitor should be running"

        # Add a test event handler
        events = []

        def test_handler(event_type, **kwargs):
            events.append((event_type, kwargs))

        api.add_observer(test_handler)

        # Setup complete, add initial content
        api.add_prefix("ex", "http://example.org/")
        api.add_axiom("ClassAssertion(ex:Person ex:Bob)")

        # Clear events
        events.clear()

        # Store hash before change
        original_hash = api._calculate_file_hash()

        # Create a second API to modify the file
        # This simulates an external application
        api2 = SimpleOwlAPI(temp_file.name)
        api2.add_axiom("ClassAssertion(ex:Person ex:Alice)")
        api2.stop()

        # Verify hash changed
        new_hash = api._calculate_file_hash()
        assert original_hash != new_hash, "File hash should have changed"

        # Manual sync for testing
        api.sync_with_file()

        # Verify change was detected
        assert len(events) > 0, "Event should have been triggered"
        assert events[0][0] == "file_changed", "Event should be 'file_changed'"

        # Verify both axioms are in the file
        axioms = api.get_all_axiom_strings()
        assert any(":Bob" in a for a in axioms), "Original axiom should be present"
        assert any(":Alice" in a for a in axioms), "New axiom should be detected"

    finally:
        # Clean up
        api.stop()
        os.unlink(temp_file.name)


def test_multiple_files():
    n = 3
    apis = []
    for _i in range(n):
        # Create a temporary OWL file for testing
        with tempfile.NamedTemporaryFile(suffix=".ofn", delete=False) as temp_file:
            temp_file.write(b"Ontology()")
            temp_file.close()

        # Initialize API
        api = SimpleOwlAPI(temp_file.name)
        api.temp_file_path = temp_file.name
        apis.append(api)
    for idx, api in enumerate(apis):
        # Add a prefix
        prefix = f"test{idx}"
        uri = f"http://test{idx}.org/"
        api.add_prefix(prefix, uri)

        # Verify prefix was added
        prefixes = api.ontology.prefix_mapping
        assert prefix in prefixes, f"Prefix {prefix} should be added"
        assert prefixes[prefix] == uri, f"URI for {prefix} should be {uri}"
    for idx, api in enumerate(apis):
        prefix = f"test{idx}"
        axiom = f"SubClassOf({prefix}:Person {prefix}:Human)"
        api.add_axiom(axiom)
        assert api.ontology.get_axioms(), f"Axioms should not be empty, idx={idx}"
        # Verify axiom was added to in-memory representation
        axioms = api.get_all_axiom_strings()
        print(f"axioms: {axioms}")
        assert len(axioms) == 1, f"Exactly one axiom should be found, idx={idx}"
        assert axiom in axioms, f"Axiom {axiom} should be added"
        axioms = api.find_axioms(prefix)
        assert len(axioms) == 1, f"Should find exactly one axiom for prefix {prefix}"
    for api in apis:
        api.stop()
        os.unlink(api.temp_file_path)
