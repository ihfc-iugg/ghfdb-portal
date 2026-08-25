"""
Shared fixtures for test_ghfdb/test_resources.

Provides the ``dataset`` fixture (re-exported from the parent conftest), an
autouse ``load_concepts`` fixture that populates the research_vocabs ``Concept``
table in the test database before any resource import tests run, and the
bibliographic fixtures T007 (specs/003-ghfdb-release-import) adds: one
``LiteratureItem`` with a known citation key, and two sharing one once case
and surrounding whitespace are normalised away.
"""

import pytest
from fairdm.factories import DatasetFactory, LiteratureItemFactory


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


@pytest.fixture
def literature_with_known_citation_key(db):
    """A bibliographic record with a known citation key (T007).

    Infrastructure for US-2's "matches exactly one record" path — built with
    the factory, per tests/README.md, since nothing about its own validation
    is under test here.
    """
    return LiteratureItemFactory(citation_key="Anderson_1978_Heat_Flow")


@pytest.fixture
def literature_with_ambiguous_citation_key(db):
    """Two bibliographic records sharing one citation key once FR-017's
    comparison rule (ignore case and surrounding whitespace) is applied, so
    a lookup on it returns two (D5, FR-020) — T007.

    ``LiteratureItem.citation_key`` is unique at the database level, so the
    two rows differ literally, by case and a trailing space, which is
    exactly the difference the release import must treat as one reference.
    """
    first = LiteratureItemFactory(citation_key="Glaeser_1983_Heat_Flow")
    second = LiteratureItemFactory(citation_key="glaeser_1983_heat_flow ")
    return first, second
