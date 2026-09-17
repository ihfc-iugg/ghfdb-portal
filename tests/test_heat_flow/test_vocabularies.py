"""Tests for ``project/heat_flow/vocabularies.py``.

The vocabularies themselves are declarative. What is worth guarding is how
their concepts reach the test database: written once when the session starts,
and never again while tests are running.
"""

import pytest

from tests.conftest import flushes_the_database, concept_preload_record


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


class TestWhichTestsEmptyTheDatabase:
    """A test that runs in a real transaction cannot be rolled back, so
    Django empties every table when it finishes — the concepts loaded at
    session start among them. ``tests/conftest.py`` writes them again after
    such a test, and recognising which tests those are is the whole of what
    it has to get right.

    Left unrecognised, the concepts go for the rest of that worker's run,
    and which tests then fail depends on how xdist happened to spread the
    suite: the same commit passed at eight workers and failed at two.

    Pinned here because the rule reads pytest-django's own fixture names,
    which a version of it is free to rename. When that happens this fails
    with the reason, rather than the suite failing somewhere else at some
    worker counts and not others.
    """

    class Node:
        """The parts of a test node the rule reads."""

        def __init__(self, fixturenames=(), marker=None):
            self.fixturenames = list(fixturenames)
            self._marker = marker

        def get_closest_marker(self, name):
            return self._marker if name == "django_db" else None

    @pytest.mark.parametrize(
        "fixturenames", [["live_server", "page"], ["transactional_db"]]
    )
    def test_a_test_asking_for_a_real_transaction_is_recognised(self, fixturenames):
        assert flushes_the_database(self.Node(fixturenames)) is True

    def test_the_transaction_argument_to_the_marker_is_recognised(self):
        node = self.Node(["db"], marker=pytest.mark.django_db(transaction=True).mark)

        assert flushes_the_database(node) is True

    def test_an_ordinary_database_test_is_not(self):
        node = self.Node(["db"], marker=pytest.mark.django_db.mark)

        assert flushes_the_database(node) is False

    def test_a_test_that_never_touches_the_database_is_not(self):
        assert flushes_the_database(self.Node()) is False


class TestEveryConceptDeclaredIsAConcept:
    """A vocabulary declares each of its concepts under its own name.

    Two concepts sharing an attribute name is silent: the class body binds
    the last one and the first never exists. It cost this vocabulary the
    two temperature-dependent conductivity functions, which the upload
    template offers and the portal then refused.
    """

    @pytest.mark.parametrize(
        "vocabulary_name",
        [
            "ConductivityPTFunction",
            "ConductivityMethod",
            "TemperatureMethod",
            "TemperatureCorrection",
            "ProbeType",
            "ExplorationMethod",
            "ExplorationPurpose",
            "GeographicEnvironment",
            "HeatFlowMethod",
            "ConductivitySource",
            "ConductivityLocation",
            "ConductivitySaturation",
            "ConductivityPTConditions",
            "ConductivityStrategy",
        ],
    )
    def test_no_two_concepts_share_a_label(self, vocabulary_name):
        """A repeated label is the symptom a shadowed declaration leaves.

        Reading the source rather than the class, because the shadowing
        happens before the class object exists — by the time the vocabulary
        can be imported, the lost concept is already gone.
        """
        import ast
        import pathlib

        import heat_flow.vocabularies as module

        tree = ast.parse(pathlib.Path(module.__file__).read_text())
        klass = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == vocabulary_name
        )
        declared = [
            target.id
            for node in klass.body
            if isinstance(node, ast.Assign)
            for target in node.targets
            if isinstance(target, ast.Name)
        ]

        duplicates = {name for name in declared if declared.count(name) > 1}
        assert not duplicates, (
            f"{vocabulary_name} declares {sorted(duplicates)} more than once; "
            "every declaration but the last is discarded"
        )


class TestTheVocabulariesCarryWhatTheTemplateOffers:
    """The upload template's dropdowns and the portal's vocabularies name
    the same concepts the same way.

    Each value below is one the assessment team's completed templates
    actually carry. A file naming one the portal spells differently is
    refused on a value its own template supplied, which is how the portal
    came to reject every file the team produced.
    """

    @pytest.mark.parametrize(
        ("vocabulary_name", "label"),
        [
            ("GeographicEnvironment", "Onshore (lake-river-etc.)"),
            ("ExplorationMethod", "Probing (onshore-lake-river-etc.)"),
            ("ExplorationMethod", "Probing (offshore-ocean)"),
            ("ExplorationMethod", "Indirect (GTM-BSR-CPD-etc.)"),
            ("ConductivityLocation", "Literature-unspecified"),
            ("ConductivityMethod", "Lab - line source - full space"),
            ("ConductivityMethod", "Lab - line source - half space"),
            ("ConductivityMethod", "Lab - plane source - full space"),
            ("ConductivityMethod", "Lab - plane source - half space"),
            ("ConductivityMethod", "Estimation - from water content-porosity"),
            ("TemperatureMethod", "HT-FTeq"),
            ("TemperatureMethod", "HT-FTpert"),
            ("ConductivityPTFunction", "T - Birch & Clark (1940)"),
            ("ConductivityPTFunction", "T - Kukkonen et al. (1999)"),
            ("ConductivityPTFunction", "T - Seipold (2001)"),
            ("ConductivityPTFunction", "T - Ratcliffe (1960)"),
            ("ConductivityPTFunction", "p - Ratcliffe (1960)"),
            ("ConductivityPTFunction", "pT - Ratcliffe (1960)"),
            ("ConductivityPTFunction", "pT - Hyndman et al. (1974)"),
            ("ConductivityMethod", "Probe - continuous heating technique"),
            ("ProbeType", "Outrigger probe (Hybrid Lister) HyLO"),
        ],
    )
    def test_the_template_value_resolves(self, db, vocabulary_name, label):
        from research_vocabs.models import Concept

        import heat_flow.vocabularies as vocabularies
        from project.ghfdb.resources.widgets import MultiConceptWidget

        vocabulary = getattr(vocabularies, vocabulary_name)
        stored = {
            concept.label.lower()
            for concept in Concept.get_for_vocabulary(vocabulary)
        }
        assert label.lower() in stored

        # And the reader resolves it in the bracketed form a cell carries.
        assert MultiConceptWidget(vocabulary).clean(f"[{label}]", row={}).count() == 1

    def test_heat_flow_method_carries_an_unspecified_concept(self, db):
        """The 2026.03 template adds an explicit "Unspecified" option to its
        heat-flow method dropdown. Checked by stored label rather than
        through ``MultiConceptWidget``: every "unspecified" token is a
        sentinel for "no value" there, by design, regardless of vocabulary,
        so a cell naming it never resolves to a concept."""
        from research_vocabs.models import Concept

        from heat_flow.vocabularies import HeatFlowMethod

        labels = {
            concept.label.lower()
            for concept in Concept.get_for_vocabulary(HeatFlowMethod)
        }
        assert "unspecified" in labels

    def test_the_three_ratcliffe_functions_are_three_concepts(self, db):
        """The surname was spelled two different wrong ways, and the
        pressure-dependent function was missing outright."""
        from research_vocabs.models import Concept

        from heat_flow.vocabularies import ConductivityPTFunction

        labels = {
            concept.label
            for concept in Concept.get_for_vocabulary(ConductivityPTFunction)
        }

        assert {
            "T - Ratcliffe (1960)",
            "p - Ratcliffe (1960)",
            "pT - Ratcliffe (1960)",
        } <= labels
        assert not [label for label in labels if "atcliff " in label or "adcliff" in label]
