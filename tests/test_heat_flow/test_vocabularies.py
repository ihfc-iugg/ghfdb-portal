# Tests for ``project/heat_flow/vocabularies/``. The vocabularies themselves are
# declarative. What is worth guarding is how their concepts reach the test database:
# written once when the session starts, and never again while tests are running.

import pytest

from tests.conftest import concept_preload_record, flushes_the_database


@pytest.fixture(scope="module")
def preload_calls_at_module_start():
    return concept_preload_record.calls


class TestConceptPreload:
    def test_concepts_are_present_without_a_per_test_fixture(self, db):
        # Nothing in this module loads concepts, and they are there anyway. Each test
        # runs inside a transaction that is rolled back afterwards, so this only holds
        # because the concepts were written before that transaction opened.
        from controlled_vocabularies.models import Record

        assert Record.objects.exists()

    @pytest.mark.parametrize("run", [1, 2, 3])
    def test_no_concepts_are_written_while_tests_run(
        self, db, run, preload_calls_at_module_start
    ):
        # Writing them costs roughly a second and several hundred queries. Spent once
        # for the session that is unremarkable; spent per test it is most of the suite's
        # runtime.
        assert concept_preload_record.calls == preload_calls_at_module_start


class TestWhichTestsEmptyTheDatabase:
    # A test that runs in a real transaction cannot be rolled back, so Django empties
    # every table when it finishes — the concepts loaded at session start among them.

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


class TestTheVocabulariesCarryWhatTheTemplateOffers:
    # The upload template's dropdowns and the portal's vocabularies name the same
    # concepts the same way. Each value below is one the assessment team's completed
    # templates actually carry.

    @pytest.mark.parametrize(
        ("vocabulary_name", "label"),
        [
            ("GEOGRAPHIC_ENVIRONMENT", "Onshore (lake-river-etc.)"),
            ("EXPLORATION_METHOD", "Probing (onshore-lake-river-etc.)"),
            ("EXPLORATION_METHOD", "Probing (offshore-ocean)"),
            ("EXPLORATION_METHOD", "Indirect (GTM-BSR-CPD-etc.)"),
            ("CONDUCTIVITY_LOCATION", "Literature-unspecified"),
            ("CONDUCTIVITY_METHOD", "Lab - line source - full space"),
            ("CONDUCTIVITY_METHOD", "Lab - line source - half space"),
            ("CONDUCTIVITY_METHOD", "Lab - plane source - full space"),
            ("CONDUCTIVITY_METHOD", "Lab - plane source - half space"),
            ("CONDUCTIVITY_METHOD", "Estimation - from water content-porosity"),
            ("TEMPERATURE_METHOD", "HT-FTeq"),
            ("TEMPERATURE_METHOD", "HT-FTpert"),
            ("CONDUCTIVITY_PT_FUNCTION", "T - Birch & Clark (1940)"),
            ("CONDUCTIVITY_PT_FUNCTION", "T - Kukkonen et al. (1999)"),
            ("CONDUCTIVITY_PT_FUNCTION", "T - Seipold (2001)"),
            ("CONDUCTIVITY_PT_FUNCTION", "T - Ratcliffe (1960)"),
            ("CONDUCTIVITY_PT_FUNCTION", "p - Ratcliffe (1960)"),
            ("CONDUCTIVITY_PT_FUNCTION", "pT - Ratcliffe (1960)"),
            ("CONDUCTIVITY_PT_FUNCTION", "pT - Hyndman et al. (1974)"),
            ("CONDUCTIVITY_METHOD", "Probe - continuous heating technique"),
            ("PROBE_TYPE", "Outrigger probe (Hybrid Lister) HyLO"),
        ],
    )
    def test_the_template_value_resolves(self, db, vocabulary_name, label):
        import heat_flow.vocabularies as vocabularies

        from project.ghfdb.resources.widgets import MultiConceptWidget

        vocabulary = getattr(vocabularies, vocabulary_name)
        stored = {
            name.lower()
            for concept in vocabularies.concepts(vocabulary)
            for name in (
                concept.display_label(),
                *(entry["@value"] for entry in concept.values("skos:hiddenLabel")),
            )
        }
        assert label.lower() in stored

        # And the reader resolves it in the bracketed form a cell carries.
        assert MultiConceptWidget(vocabulary).clean(f"[{label}]", row={}).count() == 1

    def test_heat_flow_method_carries_an_unspecified_concept(self, db):
        # The 2026.03 template adds an explicit "Unspecified" option to its heat-flow
        # method dropdown.
        from heat_flow.vocabularies import HEAT_FLOW_METHOD, concepts

        labels = {
            concept.display_label().lower() for concept in concepts(HEAT_FLOW_METHOD)
        }
        assert "unspecified" in labels

    def test_the_three_ratcliffe_functions_are_three_concepts(self, db):
        # The surname was spelled two different wrong ways, and the pressure-dependent
        # function was missing outright.
        from heat_flow.vocabularies import CONDUCTIVITY_PT_FUNCTION, concepts

        labels = {
            concept.display_label() for concept in concepts(CONDUCTIVITY_PT_FUNCTION)
        }

        assert {
            "T - Ratcliffe (1960)",
            "p - Ratcliffe (1960)",
            "pT - Ratcliffe (1960)",
        } <= labels
        assert not [
            label for label in labels if "atcliff " in label or "adcliff" in label
        ]


class TestResolveTerm:
    @pytest.mark.parametrize(
        "text",
        [
            "Onshore (continental)",
            "onshore (continental)",
            "[Onshore (continental)]",
            " [ONSHORE (CONTINENTAL)] ",
            "onshore_continental",
            "[Onshore_Continental]",
        ],
    )
    def test_a_label_or_a_key_gives_the_concept(self, db, text):
        from heat_flow.vocabularies import GEOGRAPHIC_ENVIRONMENT, resolve_term, term

        concept = resolve_term(GEOGRAPHIC_ENVIRONMENT, text)

        assert concept.uri == term(GEOGRAPHIC_ENVIRONMENT, "onshore_continental")

    @pytest.mark.parametrize("text", ["", "   ", None, "unspecified", "[Unspecified]"])
    def test_blank_and_unspecified_give_no_term(self, db, text):
        from heat_flow.vocabularies import GEOGRAPHIC_ENVIRONMENT, resolve_term

        assert resolve_term(GEOGRAPHIC_ENVIRONMENT, text) is None

    def test_an_unknown_token_is_named_in_the_error(self, db):
        from heat_flow.vocabularies import GEOGRAPHIC_ENVIRONMENT, resolve_term

        with pytest.raises(ValueError, match="swamp"):
            resolve_term(GEOGRAPHIC_ENVIRONMENT, "swamp")


class TestResolveTerms:
    def test_tokens_give_their_concepts_by_label_or_key(self, db):
        from heat_flow.vocabularies import (
            EXPLORATION_PURPOSE,
            concepts,
            identifier,
            resolve_terms,
        )

        chosen = list(concepts(EXPLORATION_PURPOSE).order_by("uri")[:2])
        labels = [concept.display_label() for concept in chosen]
        keys = [identifier(concept) for concept in chosen]
        uris = [concept.uri for concept in chosen]

        by_label = resolve_terms(
            EXPLORATION_PURPOSE, f"[{labels[0].upper()}]; {labels[1]}"
        )
        by_key = resolve_terms(EXPLORATION_PURPOSE, f"{keys[0]};{keys[1]}")

        assert sorted(by_label.values_list("uri", flat=True)) == uris
        assert sorted(by_key.values_list("uri", flat=True)) == uris

    def test_blank_gives_no_concepts(self, db):
        from heat_flow.vocabularies import EXPLORATION_PURPOSE, resolve_terms

        assert resolve_terms(EXPLORATION_PURPOSE, "").count() == 0
        assert resolve_terms(EXPLORATION_PURPOSE, " ; ").count() == 0

    def test_every_unknown_token_is_named_in_the_error(self, db):
        from heat_flow.vocabularies import EXPLORATION_PURPOSE, resolve_terms

        with pytest.raises(ValueError) as error:
            resolve_terms(EXPLORATION_PURPOSE, "swamp; [Marsh]")

        assert "swamp" in str(error.value)
        assert "Marsh" in str(error.value)
