"""
Unit tests for YAML parser error handling.

Tests handling of unavailable GHFDB spec per FR-021-A.
"""

import os
import tempfile
from pathlib import Path

import pytest


@pytest.mark.ghfdb
class TestYAMLParserErrorHandling:
    """Test YAML parser error handling for missing/invalid files."""

    def test_missing_ghfdb_spec_file_raises_clear_error(self):
        """Should raise SpecificationNotFoundError with helpful message when spec file missing."""
        from project.ghfdb.validation.yaml_parser import (
            SpecificationNotFoundError,
            parse_ghfdb_specification,
        )

        nonexistent_file = Path("/tmp/nonexistent-spec.yaml")

        with pytest.raises(SpecificationNotFoundError) as exc_info:
            parse_ghfdb_specification(nonexistent_file)

        error_message = str(exc_info.value)
        assert "not found" in error_message.lower()
        assert str(nonexistent_file) in error_message
        assert "expected file at" in error_message.lower()

    def test_invalid_yaml_format_raises_parse_error(self):
        """Should raise YAMLParseError when YAML is malformed."""
        from project.ghfdb.validation.yaml_parser import YAMLParseError, parse_ghfdb_specification

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [[[")
            f.flush()
            invalid_file = Path(f.name)

        try:
            with pytest.raises(YAMLParseError) as exc_info:
                parse_ghfdb_specification(invalid_file)

            error_message = str(exc_info.value)
            assert "failed to parse" in error_message.lower()
        finally:
            os.unlink(invalid_file)

    def test_corrupted_spec_structure_raises_validation_error(self):
        """Should raise YAMLValidationError when spec structure is incorrect."""
        from project.ghfdb.validation.yaml_parser import YAMLValidationError, parse_ghfdb_specification

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                """
# Missing required 'ghfdb_specification' top-level key
some_other_key: value
            """
            )
            f.flush()
            corrupted_file = Path(f.name)

        try:
            with pytest.raises(YAMLValidationError) as exc_info:
                parse_ghfdb_specification(corrupted_file)

            error_message = str(exc_info.value)
            assert "ghfdb_specification" in error_message.lower()
        finally:
            os.unlink(corrupted_file)

    def test_spec_missing_required_field_raises_validation_error(self):
        """Should raise YAMLValidationError with field path when required field missing."""
        from project.ghfdb.validation.yaml_parser import YAMLValidationError, parse_ghfdb_specification

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                """
ghfdb_specification:
  version: "1.0"
  publication: "Test Publication"
  release_date: "2023-01-01"
  fields:
    - name: test_field
      # Missing required 'description' field
      data_type: string
      nullable: false
      category: test
            """
            )
            f.flush()
            incomplete_file = Path(f.name)

        try:
            with pytest.raises(YAMLValidationError) as exc_info:
                parse_ghfdb_specification(incomplete_file)

            error_message = str(exc_info.value)
            assert "description" in error_message.lower()
            assert "field[0]" in error_message.lower() or "test_field" in error_message.lower()
        finally:
            os.unlink(incomplete_file)

    def test_missing_mapping_file_raises_clear_error(self):
        """Should raise SpecificationNotFoundError when mapping file missing."""
        from project.ghfdb.validation.yaml_parser import SpecificationNotFoundError, parse_field_mappings

        nonexistent_file = Path("/tmp/nonexistent-mappings.yaml")

        with pytest.raises(SpecificationNotFoundError) as exc_info:
            parse_field_mappings(nonexistent_file)

        error_message = str(exc_info.value)
        assert "not found" in error_message.lower()
        assert "field mapping" in error_message.lower()

    def test_invalid_relationship_type_raises_validation_error(self):
        """Should raise YAMLValidationError for invalid relationship_type enum value."""
        from project.ghfdb.validation.yaml_parser import YAMLValidationError, parse_field_mappings

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                """
ghfdb_fields:
  - name: test_field
    django_model: TestModel
    django_field: test_field
    relationship_type: invalid_type
    nullable: false
    accessor_path: model.field
    orm_example: TestModel.objects.all()
            """
            )
            f.flush()
            invalid_file = Path(f.name)

        try:
            with pytest.raises((YAMLValidationError, ValueError)):
                parse_field_mappings(invalid_file)
        finally:
            os.unlink(invalid_file)
