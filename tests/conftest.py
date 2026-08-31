"""
Configuration for pytest.
"""

import os

import django
import pytest


def pytest_configure():
    """Configure Django for testing."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    os.environ.setdefault("DJANGO_ENV", "development")
    django.setup()


class ConceptPreloadRecord:
    """How many times the vocabulary concepts have been written this session.

    Loading them is expensive — seventeen vocabularies and several hundred
    concepts, each written with its own query — so it happens once, in
    ``django_db_setup`` below. ``tests/test_heat_flow/test_vocabularies.py``
    asserts against this record, because the constitution asks for a
    deterministic guard on performance rather than a wall-clock measurement.
    """

    def __init__(self) -> None:
        self.calls = 0


concept_preload_record = ConceptPreloadRecord()


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Load every vocabulary concept once, for the whole session.

    Each test runs inside a transaction that is rolled back afterwards, so
    anything written from inside a test is gone before the next one starts.
    Writing the concepts here instead — outside that transaction, while the
    database is unblocked — puts them in the database the tests roll back
    *to*, where they survive every rollback and are written once rather than
    once per test.

    ``Concept.preload()`` writes the vocabularies registered in
    ``research_vocabs``' global registry, and registration is normally a side
    effect of a model field's own ``__init__``. ``ConceptManyToManyField``
    does this; the single-valued ``ConceptField`` does not, because its
    registration call is commented out upstream in
    ``research_vocabs.fields.BaseConceptField.__init__``. ``environment`` and
    ``explo_method`` on ``HeatFlowSite`` are both ``ConceptField``, so their
    two vocabularies are registered by hand here. Without that, their concepts
    never load and every filter or fixture depending on them finds nothing.
    """
    from research_vocabs import registry
    from research_vocabs.models import Concept

    from heat_flow.vocabularies import ExplorationMethod, GeographicEnvironment

    preload = Concept.preload.__func__

    def counted_preload(cls: type[Concept]) -> None:
        concept_preload_record.calls += 1
        preload(cls)

    Concept.preload = classmethod(counted_preload)

    for vocabulary in (GeographicEnvironment, ExplorationMethod):
        registry.register(vocabulary())

    with django_db_blocker.unblock():
        Concept.preload()
