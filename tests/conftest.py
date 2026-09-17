"""
Configuration for pytest.
"""

import importlib.util
import os
from pathlib import Path

import django
import pytest


def pytest_configure():
    """Configure Django for testing."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    os.environ.setdefault("DJANGO_ENV", "development")
    django.setup()


def _browser_is_installed():
    """True when Playwright is importable *and* its browser is downloaded.

    Testing the import alone is not enough: installing the package is one
    step and downloading the browser is another, and a runner with the
    dependency but no download errors at launch instead of skipping.
    """
    if importlib.util.find_spec("playwright") is None:
        return False

    from playwright.sync_api import sync_playwright

    try:
        with sync_playwright() as p:
            return Path(p.chromium.executable_path).exists()
    except Exception:
        return False


def _should_skip_browser_tests(has_browser, env):
    """Decide whether browser-marked tests skip, given the browser and the environment.

    Locally a missing browser is ordinary: a contributor who has not run
    ``playwright install`` should see skips, not a wall of errors. In CI it
    is a failure — a runner that never downloaded a browser must error, not
    quietly skip, or the check reads green for a test that never ran.
    """
    if has_browser:
        return False
    return env.get("CI", "").lower() not in {"1", "true"}


HAS_BROWSER = _browser_is_installed()

requires_browser = pytest.mark.skipif(
    _should_skip_browser_tests(HAS_BROWSER, os.environ),
    reason="playwright browser not installed (run: playwright install chromium)",
)


class ConceptPreloadRecord:
    """How many times the vocabulary concepts have been written this session.

    Loading them is expensive — seventeen vocabularies and several hundred
    concepts, each written with its own query — so it happens once, in
    ``django_db_setup`` below. ``tests/test_heat_flow/test_vocabularies.py``
    asserts against this record, because the constitution asks for a
    deterministic guard on performance rather than a wall-clock measurement.

    ``restores`` counts the separate, rarer case of writing them again after
    a test truncated them, which ``vocabulary_concepts_outlive_a_flush``
    below explains. Counted apart from ``calls`` so the guard on per-test
    loading still means what it says: a restore is not a test paying for its
    own concepts, and a test that is not transactional must never cause one.
    """

    def __init__(self) -> None:
        self.calls = 0
        self.restores = 0
        self.write_concepts = None


concept_preload_record = ConceptPreloadRecord()


def flushes_the_database(item) -> bool:
    """Whether this test truncates the database when it finishes.

    True for a test that asked for a real transaction — directly, through
    ``transactional_db``, or through ``live_server``, which is built on one.
    Django's ``TransactionTestCase`` cannot roll such a test back, so it
    empties every table instead.
    """
    if {"live_server", "transactional_db"} & set(item.fixturenames):
        return True

    marker = item.get_closest_marker("django_db")
    if marker is None:
        return False
    if marker.args and marker.args[0]:
        return True
    return bool(marker.kwargs.get("transaction"))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_teardown(item):
    """Write the vocabulary concepts again after a test that truncated them.

    A test that runs in a real transaction cannot be rolled back, so Django
    empties every table when it finishes. The concepts ``django_db_setup``
    wrote belong to no test's transaction, so that flush takes them for
    good, and every later test on the same worker then finds an empty
    vocabulary — a factory choosing from no concepts, or an import refusing
    a value its own vocabulary should carry.

    Which tests those are depends on how xdist happened to spread the suite
    across workers, so the suite passed at one worker count and failed at
    another on the same commit.

    A hook rather than a fixture: fixtures are torn down in reverse order of
    setup, so any fixture of ours would finish before the flush it is there
    to undo. This runs after every fixture for the test has been torn down,
    which is the only point at which the table is known to be empty.
    """
    yield

    if concept_preload_record.write_concepts is None:
        return
    if not flushes_the_database(item):
        return

    from pytest_django.plugin import blocking_manager_key

    concept_preload_record.restores += 1
    with item.config.stash[blocking_manager_key].unblock():
        concept_preload_record.write_concepts()


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
    from heat_flow.vocabularies import ExplorationMethod, GeographicEnvironment
    from research_vocabs import registry
    from research_vocabs.models import Concept

    preload = Concept.preload.__func__

    def counted_preload(cls: type[Concept]) -> None:
        concept_preload_record.calls += 1
        preload(cls)

    Concept.preload = classmethod(counted_preload)

    # The uncounted original, for restoring after a flush. A restore is not a
    # test loading its own concepts, which is what ``calls`` is there to
    # catch, so it is recorded under ``restores`` instead.
    concept_preload_record.write_concepts = lambda: preload(Concept)

    for vocabulary in (GeographicEnvironment, ExplorationMethod):
        registry.register(vocabulary())

    with django_db_blocker.unblock():
        Concept.preload()
