import os
import tempfile

from owl_mcp.owl_api import SimpleOwlAPI


def test_concurrent_instances():
    """Test multiple API instances pointing to the same file."""
    # Create a temporary OWL file for testing
    with tempfile.NamedTemporaryFile(suffix=".ofn", delete=False) as temp_file:
        temp_file.write(b"""Ontology()
""")
        temp_file.close()

    # Initialize first API instance
    api1 = SimpleOwlAPI(temp_file.name)

    # Track events for the first instance
    events1 = []

    def on_event1(event_type, **kwargs):
        events1.append((event_type, kwargs))

    api1.add_observer(on_event1)

    # Initialize second API instance pointing to the same file
    api2 = SimpleOwlAPI(temp_file.name)

    # Track events for the second instance
    events2 = []

    def on_event2(event_type, **kwargs):
        events2.append((event_type, kwargs))

    api2.add_observer(on_event2)

    try:
        # Add a prefix through first API
        api1.add_prefix("ex", "http://example.org/")

        # Add an axiom using the first instance
        axiom1 = "ClassAssertion(ex:Person ex:John)"
        api1.add_axiom(axiom1)

        # Clear events
        events1.clear()
        events2.clear()

        # Sync the second instance - it should detect the change
        api2.sync_with_file()

        # The second instance should see the axiom added by the first
        axioms2 = api2.get_all_axiom_strings()
        assert axiom1 in axioms2, "Second instance should see axiom added by first instance"

        # Add an axiom using the second instance
        axiom2 = "ClassAssertion(ex:Person ex:Jane)"
        api2.add_axiom(axiom2)

        # Clear events again
        events1.clear()
        events2.clear()

        # Sync the first instance - it should detect the change
        api1.sync_with_file()

        # The first instance should see the axiom added by the second
        axioms1 = api1.get_all_axiom_strings()
        assert axiom2 in axioms1, "First instance should see axiom added by second instance"

        # Verify both axioms are present in both instances
        assert axiom1 in axioms1, "First axiom should be in first instance"
        assert axiom2 in axioms1, "Second axiom should be in first instance"

        axioms2 = api2.get_all_axiom_strings()
        assert axiom1 in axioms2, "First axiom should be in second instance"
        assert axiom2 in axioms2, "Second axiom should be in second instance"

    finally:
        # Clean up
        api1.stop()
        api2.stop()
        os.unlink(temp_file.name)


def test_hash_calculation():
    """Test that file hash calculation works correctly."""
    # Create a temporary OWL file for testing
    with tempfile.NamedTemporaryFile(suffix=".ofn", delete=False) as temp_file:
        temp_file.write(b"""Ontology()
""")
        temp_file.close()

    try:
        # Initialize API
        api = SimpleOwlAPI(temp_file.name)

        # Get original hash
        original_hash = api.file_hash
        assert original_hash, "File hash should be calculated"

        # Modify the file using the API (this should update the hash)
        api.add_prefix("ex", "http://example.org/")
        api.add_axiom("ClassAssertion(ex:Person ex:John)")

        # Check that hash was updated
        assert api.file_hash != original_hash, "Hash should be updated after modification"

        # Get current hash for comparison
        current_hash = api.file_hash

        # Make a second API instance and check hash
        api2 = SimpleOwlAPI(temp_file.name)
        assert api2.file_hash == current_hash, "Hash should be the same for both instances"

        # Clean up second instance
        api2.stop()

        # Stop the API
        api.stop()
    finally:
        # Clean up
        os.unlink(temp_file.name)


def test_file_monitoring_setup():
    """Test that file monitoring is set up correctly."""
    # Create a temporary OWL file for testing
    with tempfile.NamedTemporaryFile(suffix=".ofn", delete=False) as temp_file:
        temp_file.write(b"""Ontology()
""")
        temp_file.close()

    try:
        # Initialize API
        api = SimpleOwlAPI(temp_file.name)

        # Verify that file_monitor is initialized
        assert api.file_monitor is not None, "File monitor should be initialized"

        # Try stopping and restarting monitoring
        monitor = api.file_monitor
        api.stop()

        # Verify monitor was stopped
        assert not monitor.is_alive(), "Monitor should be stopped after api.stop()"

    finally:
        # Clean up
        os.unlink(temp_file.name)
