import importlib.util
import os
import uuid
from pathlib import Path

import pytest


def pytest_configure():
    """Swap in settings a test can change after Django is set up.

    pytest-django has already set Django up by the time this runs, from the
    settings module and environment named in pyproject.toml. A setting read
    while the apps load belongs in config/development.py instead.
    """
    from django.conf import settings

    # Argon2 spends a tenth of a second on every password it hashes, by design. A test
    # needs a password stored, not one that resists cracking. Django builds its list of
    # hashers the first time it hashes, which is after this.
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


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

    Loading them is expensive — every vocabulary file the portal ships is
    parsed and several thousand concepts written — so it happens once, in
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
    # Load every vocabulary concept once, for the whole session. Each test runs inside a
    # transaction that is rolled back afterwards, so anything written from inside a test
    # is gone before the next one starts.
    from controlled_vocabularies.management.commands.sync_vocabularies import Command
    from django.core.management import call_command

    handle = Command.handle

    def counted_handle(self, *args, **options):
        concept_preload_record.calls += 1
        return handle(self, *args, **options)

    Command.handle = counted_handle

    def write_concepts():
        # The uncounted original, for restoring after a flush. A restore is not a
        # test loading its own concepts, which is what ``calls`` is there to
        # catch, so it is recorded under ``restores`` instead.
        Command.handle = handle
        try:
            call_command("sync_vocabularies", verbosity=0)
        finally:
            Command.handle = counted_handle

    concept_preload_record.write_concepts = write_concepts

    with django_db_blocker.unblock():
        keep_autovacuum_off_the_test_tables()
        call_command("sync_vocabularies", verbosity=0)


def keep_autovacuum_off_the_test_tables():
    """Stop PostgreSQL gathering planner statistics on the test database.

    Autovacuum analyses a table once enough rows have changed, which in a test
    run means whatever a test that committed happened to leave behind: a column
    that was empty, or every row in one dataset. A later test that writes a
    hundred rows inside its own transaction is then planned as if it had one,
    and the nested loops the planner picks for the visibility subqueries take
    minutes. Without statistics the planner falls back on its defaults, and the
    same tests take seconds. A table the connecting user does not own
    (PostGIS's ``spatial_ref_sys`` on some servers) is left alone.
    """
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute(
            """
            DO $$
            DECLARE test_table record;
            BEGIN
                FOR test_table IN
                    SELECT schemaname, tablename FROM pg_tables
                    WHERE schemaname = 'public' AND tableowner = current_user
                LOOP
                    EXECUTE format(
                        'ALTER TABLE %I.%I SET (autovacuum_enabled = false)',
                        test_table.schemaname,
                        test_table.tablename
                    );
                END LOOP;
            END $$;
            """
        )


@pytest.fixture(autouse=True)
def fresh_api_rate_limits(monkeypatch):
    # The API's rate limits count requests per caller in a cache that outlives a
    # test, so a worker that runs many anonymous API tests within a minute is
    # refused with 429 by tests that came before it. Each test counts from zero
    # in a cache of its own. The vocabulary graphs stay in the shared cache.
    from django.core.cache.backends.locmem import LocMemCache
    from rest_framework.throttling import SimpleRateThrottle

    monkeypatch.setattr(
        SimpleRateThrottle, "cache", LocMemCache(f"throttle-{id(object())}", {})
    )


@pytest.fixture
def empty_database():
    """Create an empty database on the suite's PostgreSQL server, and drop it after.

    Yields:
        The default connection's settings with ``NAME`` set to the new database.
    """
    import psycopg2
    from django.conf import settings

    server = settings.DATABASES["default"]
    name = f"ghfdb_migrate_{uuid.uuid4().hex}"
    maintenance = psycopg2.connect(
        dbname="postgres",
        user=server["USER"],
        password=server["PASSWORD"],
        host=server["HOST"],
        port=server["PORT"],
    )
    maintenance.autocommit = True
    with maintenance.cursor() as cursor:
        cursor.execute(f'CREATE DATABASE "{name}"')
    yield {**server, "NAME": name}
    with maintenance.cursor() as cursor:
        cursor.execute(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)')
    maintenance.close()


@pytest.fixture
def published_dataset(db):
    """A dataset anyone may open: public and published."""
    from fairdm.factories import DatasetFactory
    from fairdm.utils.choices import Visibility

    return DatasetFactory(visibility=Visibility.PUBLIC, published=True)


@pytest.fixture
def unpublished_dataset(db):
    """A dataset only its team may open: public but not yet published."""
    from fairdm.factories import DatasetFactory
    from fairdm.utils.choices import Visibility

    return DatasetFactory(visibility=Visibility.PUBLIC, published=False)


@pytest.fixture
def member(unpublished_dataset):
    """A signed-in person who may view the unpublished dataset."""
    from fairdm.contrib.contributors.choices import ContributionLevel
    from fairdm.factories import ContributionFactory, PersonFactory

    person = PersonFactory(is_claimed=True, password="test-pass-123")
    ContributionFactory(
        contributor=person,
        content_object=unpublished_dataset,
        level=ContributionLevel.VIEW,
    )
    return person


@pytest.fixture
def page_records(published_dataset):
    """A child with every record its page names, all in the published dataset."""
    from heat_flow.vocabularies import EXPLORATION_METHOD, term

    from tests.factories import (
        HeatFlowFactory,
        HeatFlowIntervalFactory,
        HeatFlowSiteFactory,
        IntervalConductivityFactory,
        ParentHeatFlowFactory,
        ThermalGradientFactory,
    )

    # The exploration method decides whether a measurement can be scored at all, so it
    # is set rather than left to the factory's random choice.
    site = HeatFlowSiteFactory(
        dataset=published_dataset, explo_method_id=term(EXPLORATION_METHOD, "drilling")
    )
    interval = HeatFlowIntervalFactory(
        dataset=published_dataset, site=site, top=0, bottom=500
    )
    gradient = ThermalGradientFactory(dataset=published_dataset, sample=interval)
    conductivity = IntervalConductivityFactory(
        dataset=published_dataset, sample=interval
    )
    parent = ParentHeatFlowFactory(dataset=published_dataset, sample=site)
    child = HeatFlowFactory(
        dataset=published_dataset,
        sample=interval,
        thermal_gradient=gradient,
        thermal_conductivity=conductivity,
        parent=parent,
    )
    return {
        "site": site,
        "interval": interval,
        "gradient": gradient,
        "conductivity": conductivity,
        "parent": parent,
        "child": child,
    }


@pytest.fixture
def hide(unpublished_dataset):
    """Return a function that moves a record into the unpublished dataset."""

    def move(record):
        type(record).objects.filter(pk=record.pk).update(dataset=unpublished_dataset)
        record.refresh_from_db()

    return move
