"""
Shared fixtures for test_ghfdb/test_resources.

Provides the ``dataset`` fixture (re-exported from the parent conftest) and an
autouse ``load_concepts`` fixture that populates the research_vocabs ``Concept``
table in the test database before any resource import tests run.
"""

import pytest
from fairdm.factories import DatasetFactory


@pytest.fixture
def dataset():
    """A minimal FairDM Dataset — infrastructure, not under test."""
    return DatasetFactory()


@pytest.fixture(autouse=True)
def load_concepts(db):
    """Ensure all vocabulary concepts are in the test DB before each test."""
    from research_vocabs.models import Concept

    if not Concept.objects.exists():
        Concept.preload()
