"""
Configuration for pytest.

This file configures the test environment for Django and defines shared fixtures
for the testing infrastructure.
"""

import os
from pathlib import Path

import django
import pytest
from django.core.management import call_command
from fairdm.core.models import Dataset


def pytest_configure():
    """Configure Django for testing."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    os.environ.setdefault("DJANGO_ENV", "development")
    django.setup()


# =============================================================================
# File Loading Helpers
# =============================================================================

def get_file(filename):
    """
    Helper function to load test data files.
    
    Args:
        filename: Relative or absolute path to the file
        
    Returns:
        bytes: File contents as binary data
    """
    path = Path(filename)
    if not path.is_absolute():
        # Resolve relative to project root
        path = Path(__file__).parent.parent / filename
    
    with open(path, "rb") as f:
        return f.read()


# =============================================================================
# Excel Fixture Loaders
# =============================================================================

@pytest.fixture
def minimal_ghfdb_import_data():
    """
    Load minimal GHFDB import fixture.
    
    Provides 5 heat flow sites with complete mandatory fields for basic
    import functionality testing.
    
    Returns:
        bytes: Excel file contents
    """
    return get_file("tests/fixtures/minimal_ghfdb_import.xlsx")


@pytest.fixture
def invalid_ghfdb_import_data():
    """
    Load invalid GHFDB import fixture for error testing.
    
    Contains 5 deliberately invalid records to test validation error handling:
    - Missing mandatory field (name)
    - Out-of-bounds latitude (>90)
    - Negative heat flow value
    - Missing environment field
    - Inconsistent depth values (top > bottom)
    
    Returns:
        bytes: Excel file contents
    """
    return get_file("tests/fixtures/invalid_ghfdb_import.xlsx")


@pytest.fixture
def round_trip_reference_data():
    """
    Load comprehensive round-trip reference fixture.
    
    Provides 10 heat flow sites covering all field types, controlled vocabularies,
    and optional fields for export→import roundtrip integrity testing.
    
    Returns:
        bytes: Excel file contents
    """
    return get_file("tests/fixtures/round_trip_reference.xlsx")


# =============================================================================
# Django JSON Fixture Loaders
# =============================================================================

@pytest.fixture
def review_submission_dataset(django_db_blocker):
    """
    Load review submission workflow fixture.
    
    Provides a Dataset in "pending review" state with:
    - Project (pk=100)
    - Dataset (pk=100, visibility=0/private)
    - Dataset descriptions and dates
    - No review object (awaiting review)
    
    Returns:
        Dataset: The loaded dataset instance
    """
    with django_db_blocker.unblock():
        call_command('loaddata', 'review_submission_dataset.json', verbosity=0)
    return Dataset.objects.get(pk=100)


@pytest.fixture
def admin_approval_dataset(django_db_blocker):
    """
    Load approved dataset with review fixture.
    
    Provides a Dataset in "reviewed and approved" state with:
    - Project (pk=200, status=completed)
    - Dataset (pk=200, visibility=1/public)
    - Complete review object (pk=200, status=2/complete)
    - Review dates and comments
    
    Returns:
        Dataset: The loaded dataset instance
    """
    with django_db_blocker.unblock():
        call_command('loaddata', 'admin_approval_dataset.json', verbosity=0)
    return Dataset.objects.get(pk=200)


# =============================================================================
# Shared Test Utilities
# =============================================================================

@pytest.fixture
def ghfdb_dataset(db):
    """
    Create a basic test dataset for GHFDB import operations.
    
    Returns:
        Dataset: A new dataset instance named "Test Dataset"
    """
    return Dataset.objects.create(name="Test Dataset")
