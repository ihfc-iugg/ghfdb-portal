"""Tests for ``project/heat_flow/vocabularies.py``.

The vocabularies themselves are declarative. What is worth guarding is how
their concepts reach the test database: written once when the session starts,
and never again while tests are running.
"""

import pytest

from tests.conftest import concept_preload_record


@pytest.fixture(scope="module")
def preload_calls_at_module_start():
    """How many times the concepts had been written when this module began."""
    return concept_preload_record.calls


class TestConceptPreload:
    """The vocabulary concepts are written once per session, not per test."""

    def test_concepts_are_present_without_a_per_test_fixture(self, db):
        """Nothing in this module loads concepts, and they are there anyway.

        Each test runs inside a transaction that is rolled back afterwards, so
        this only holds because the concepts were written before that
        transaction opened.
        """
        from research_vocabs.models import Concept

        assert Concept.objects.exists()

    @pytest.mark.parametrize("run", [1, 2, 3])
    def test_no_concepts_are_written_while_tests_run(
        self, db, run, preload_calls_at_module_start
    ):
        """Writing them costs roughly a second and several hundred queries.

        Spent once for the session that is unremarkable; spent per test it is
        most of the suite's runtime. Counting the writes catches that where a
        stopwatch cannot, since the count is the same on a fast machine and a
        slow one. Three runs rather than one because a per-test write only
        shows up as a difference between two tests.
        """
        assert concept_preload_record.calls == preload_calls_at_module_start
