"""
Shared fixtures for test_ghfdb/test_resources.

Provides the ``dataset`` fixture, re-exported from the parent conftest. The
vocabulary concepts these tests read are written once for the session, in
``tests/conftest.py``.
"""

import pytest
from fairdm.factories import DatasetFactory


@pytest.fixture
def dataset(db):
    """A minimal FairDM Dataset — infrastructure, not under test."""
    return DatasetFactory()
