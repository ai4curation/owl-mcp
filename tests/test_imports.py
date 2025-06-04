import os

import pytest

from owl_mcp.owl_api import SimpleOwlAPI


@pytest.mark.parametrize("extended_base_name", ["extended"])
def test_ontology_imports(extended_base_name):
    """Test that ontology imports work correctly.

    Currently incomplete; see: https://github.com/ontology-tools/py-horned-owl/issues/43
    """
    # Get the path to our test ontologies
    test_dir = os.path.dirname(__file__)
    core_path = os.path.join(test_dir, "input", "core.ofn")
    extended_path = os.path.join(test_dir, "input", f"{extended_base_name}.ofn")

    # Verify test files exist
    assert os.path.exists(core_path), f"Core ontology not found at {core_path}"
    assert os.path.exists(extended_path), f"Extended ontology not found at {extended_path}"

    # Load the core ontology
    core_api = SimpleOwlAPI(core_path, serialization="ofn")

    # Load the extended ontology (which imports core)
    extended_api = SimpleOwlAPI(extended_path, serialization="ofn")

    assert len(extended_api.import_map.values()) == 2, (
        "Should have two ontologies (self+core) in the import map"
    )

    try:
        # Test that core ontology has expected classes
        core_axioms = core_api.get_all_axiom_strings()
        core_axiom_str = "\n".join(core_axioms)

        assert "core:Animal" in core_axiom_str
        assert "core:Mammal" in core_axiom_str
        assert "core:Dog" in core_axiom_str
        assert "core:Cat" in core_axiom_str

        # Test that extended ontology has both its own classes and imported classes
        extended_axioms = extended_api.get_all_axiom_strings()

        import_axioms = extended_api.find_axioms(None, axiom_type="Import")
        assert len(import_axioms) > 0, "Should find imported axioms"
        for axiom in import_axioms:
            print(f"Imported axiom: {axiom}")

        extended_axiom_str = "\n".join(extended_axioms)
        print(extended_axiom_str)

        # Should have extended ontology's own classes
        assert "ext:Person" in extended_axiom_str
        assert "ext:Pet" in extended_axiom_str
        assert "ext:John" in extended_axiom_str
        assert "ext:Fido" in extended_axiom_str

        # Should also have core classes due to import
        # Note: This depends on how py-horned-owl handles imports
        # The imported axioms might not show up in get_all_axiom_strings()

        # Test using regex patterns to find specific axioms
        person_axioms = extended_api.find_axioms(r"ext:Person")
        assert len(person_axioms) > 0, "Should find axioms about ext:Person"

        pet_axioms = extended_api.find_axioms(r"ext:Pet")
        assert len(pet_axioms) > 0, "Should find axioms about ext:Pet"

        # Test finding axioms that use imported classes
        # TODO: should also find imported axioms
        mammal_axioms = extended_api.find_axioms(r"core:Mammal")
        assert len(mammal_axioms) > 0, "Should find axioms using imported core:Mammal class"
        for axiom in mammal_axioms:
            print(f"Mammal axiom: {axiom}")

        # Test finding specific individuals
        fido_axioms = extended_api.find_axioms(r"ext:Fido")
        assert len(fido_axioms) > 0, "Should find axioms about Fido"

        # Test that we can find data property assertions using imported properties
        age_axioms = extended_api.find_axioms(r"core:hasAge")
        assert len(age_axioms) > 0, "Should find axioms using imported core:hasAge property"

        print(f"Core ontology has {len(core_axioms)} axioms")
        print(f"Extended ontology has {len(extended_axioms)} axioms")
        print(f"Found {len(person_axioms)} axioms about ext:Person")
        print(f"Found {len(mammal_axioms)} axioms about core:Mammal")
        print(f"Found {len(age_axioms)} axioms using core:hasAge")

        # labels
        labels = extended_api.get_labels_for_iri("core:Mammal", include_imports=True)
        assert labels == ["Mammal"], "Should find label for core:Mammal if include_imports is True"
        labels = extended_api.get_labels_for_iri("core:Mammal")
        assert labels == ["Mammal"], "Should find label for core:Mammal if include_imports is True"
        labels = extended_api.get_labels_for_iri("core:Mammal", include_imports=False)
        assert labels == [], "Should not find label for core:Mammal if include_imports is False"

    finally:
        # Cleanup
        core_api.stop()
        extended_api.stop()


def test_find_axioms_across_imports():
    """Test regex pattern matching across imported ontologies."""
    test_dir = os.path.dirname(__file__)
    extended_path = os.path.join(test_dir, "input", "extended.ofn")

    extended_api = SimpleOwlAPI(extended_path, serialization="ofn")

    try:
        # Test various regex patterns

        # Find all class assertions
        class_assertions = extended_api.find_axioms(r"^ClassAssertion")
        assert len(class_assertions) > 0, "Should find ClassAssertion axioms"

        # Find all axioms mentioning dogs (from imported ontology)
        dog_axioms = extended_api.find_axioms(r"core:Dog")
        assert len(dog_axioms) > 0, "Should find axioms about dogs"

        # Find all data property assertions with integer values
        int_data_props = extended_api.find_axioms(r'"\d+".*xsd:int')
        assert len(int_data_props) > 0, "Should find integer data property assertions"

        # Find all annotation assertions with English labels
        en_labels = extended_api.find_axioms(r'"[^"]*"@en')
        assert len(en_labels) > 0, "Should find English label annotations"

        # Test case-insensitive matching for names
        name_axioms = extended_api.find_axioms(r"(?i)fido|whiskers|john")
        assert len(name_axioms) > 0, "Should find axioms with names (case insensitive)"

        print(f"Found {len(class_assertions)} ClassAssertion axioms")
        print(f"Found {len(dog_axioms)} axioms about dogs")
        print(f"Found {len(int_data_props)} integer data properties")
        print(f"Found {len(en_labels)} English labels")
        print(f"Found {len(name_axioms)} axioms with names")

    finally:
        extended_api.stop()


def test_invalid_regex_with_imports():
    """Test that invalid regex patterns still raise errors with imported ontologies."""
    test_dir = os.path.dirname(__file__)
    extended_path = os.path.join(test_dir, "input", "extended.ofn")

    extended_api = SimpleOwlAPI(extended_path, serialization="ofn")

    try:
        # Test invalid regex
        with pytest.raises(Exception):  # Should raise re.error
            extended_api.find_axioms("[invalid_regex")

    finally:
        extended_api.stop()
