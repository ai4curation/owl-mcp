import os
import tempfile

import pytest

from owl_mcp.xml_catalog_utils import (
    find_catalog_file,
    load_catalog_for_ontology,
    read_catalog,
    resolve_iri,
)


def test_read_catalog():
    """Test reading a simple XML catalog."""
    catalog_content = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<catalog prefer="public" xmlns="urn:oasis:names:tc:entity:xmlns:xml:catalog">
    <uri name="http://example.org/ontology.owl" uri="local/ontology.owl"/>
    <uri name="http://example.org/imports/base.owl" uri="imports/base.owl"/>
    <uri id="test" name="http://test.org/test.owl" uri="../test.owl"/>
</catalog>"""

    with tempfile.TemporaryDirectory() as tmpdir:
        catalog_path = os.path.join(tmpdir, "catalog.xml")
        with open(catalog_path, "w") as f:
            f.write(catalog_content)

        mappings = read_catalog(catalog_path)

        assert len(mappings) == 3
        assert "http://example.org/ontology.owl" in mappings
        assert "http://example.org/imports/base.owl" in mappings
        assert "http://test.org/test.owl" in mappings

        # Check that relative paths are resolved
        assert mappings["http://example.org/ontology.owl"] == os.path.join(
            tmpdir, "local", "ontology.owl"
        )
        assert mappings["http://example.org/imports/base.owl"] == os.path.join(
            tmpdir, "imports", "base.owl"
        )
        assert mappings["http://test.org/test.owl"] == os.path.normpath(
            os.path.join(tmpdir, "..", "test.owl")
        )


def test_catalog_without_namespace():
    """Test reading catalog that might not have proper namespace declaration."""
    catalog_content = """<?xml version="1.0" encoding="UTF-8"?>
<catalog>
    <uri name="http://example.org/simple.owl" uri="simple.owl"/>
</catalog>"""

    with tempfile.TemporaryDirectory() as tmpdir:
        catalog_path = os.path.join(tmpdir, "catalog.xml")
        with open(catalog_path, "w") as f:
            f.write(catalog_content)

        mappings = read_catalog(catalog_path)

        assert len(mappings) == 1
        assert "http://example.org/simple.owl" in mappings


def test_find_catalog_file():
    """Test finding catalog files in directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test with default catalog names
        catalog_path = os.path.join(tmpdir, "catalog.xml")
        with open(catalog_path, "w") as f:
            f.write('<?xml version="1.0"?><catalog></catalog>')

        found_path = find_catalog_file(tmpdir)
        assert found_path == catalog_path

        # Test with custom catalog names
        custom_catalog = os.path.join(tmpdir, "my-catalog.xml")
        with open(custom_catalog, "w") as f:
            f.write('<?xml version="1.0"?><catalog></catalog>')

        found_path = find_catalog_file(tmpdir, ["my-catalog.xml"])
        assert found_path == custom_catalog

        # Test when no catalog exists
        empty_dir = os.path.join(tmpdir, "empty")
        os.makedirs(empty_dir)
        found_path = find_catalog_file(empty_dir)
        assert found_path is None


def test_resolve_iri():
    """Test IRI resolution."""
    mappings = {
        "http://example.org/test.owl": "/path/to/test.owl",
        "http://example.org/base.owl": "/path/to/base.owl",
    }

    assert resolve_iri("http://example.org/test.owl", mappings) == "/path/to/test.owl"
    assert resolve_iri("http://example.org/missing.owl", mappings) is None


def test_load_catalog_for_ontology():
    """Test loading catalog for an ontology file."""
    catalog_content = """<?xml version="1.0" encoding="UTF-8"?>
<catalog xmlns="urn:oasis:names:tc:entity:xmlns:xml:catalog">
    <uri name="http://example.org/dep.owl" uri="dep.owl"/>
</catalog>"""

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create ontology file and catalog in same directory
        ontology_path = os.path.join(tmpdir, "main.owl")
        with open(ontology_path, "w") as f:
            f.write("# Dummy ontology")

        catalog_path = os.path.join(tmpdir, "catalog.xml")
        with open(catalog_path, "w") as f:
            f.write(catalog_content)

        mappings = load_catalog_for_ontology(ontology_path)

        assert len(mappings) == 1
        assert "http://example.org/dep.owl" in mappings
        assert mappings["http://example.org/dep.owl"] == os.path.join(tmpdir, "dep.owl")


def test_nonexistent_catalog():
    """Test error handling for nonexistent catalog."""
    with pytest.raises(FileNotFoundError):
        read_catalog("/path/that/does/not/exist/catalog.xml")


def test_invalid_xml():
    """Test error handling for invalid XML."""
    with tempfile.TemporaryDirectory() as tmpdir:
        catalog_path = os.path.join(tmpdir, "invalid.xml")
        with open(catalog_path, "w") as f:
            f.write("This is not XML")

        with pytest.raises(Exception):  # Could be ParseError or similar
            read_catalog(catalog_path)
