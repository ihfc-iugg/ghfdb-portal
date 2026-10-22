# Tests for ``project/heat_flow/forms.py`` (FS-009): the shared form pieces and the six
# forms a researcher corrects heat flow records with.

import pytest
from django.core.exceptions import ValidationError


class TestConceptTextField:
    @pytest.fixture
    def environment(self):
        from heat_flow.forms import ConceptTextField
        from heat_flow.models import HeatFlowSite

        return ConceptTextField(HeatFlowSite._meta.get_field("environment"))

    @pytest.fixture
    def purposes(self):
        from heat_flow.forms import ConceptTextField
        from heat_flow.models import HeatFlowSite

        return ConceptTextField(HeatFlowSite._meta.get_field("explo_purpose"))

    @pytest.fixture
    def two_purposes(self, db):
        from heat_flow.vocabularies import ExplorationPurpose
        from research_vocabs.models import Concept

        return list(Concept.get_for_vocabulary(ExplorationPurpose).order_by("name")[:2])

    def test_a_stored_term_is_drawn_as_its_label(self, environment):
        from heat_flow.vocabularies import GeographicEnvironment

        label = dict(GeographicEnvironment().choices)["onshore_continental"]

        assert environment.prepare_value("onshore_continental") == label

    def test_several_stored_terms_are_drawn_joined_by_semicolons(
        self, purposes, two_purposes
    ):
        drawn = purposes.prepare_value(two_purposes)

        assert drawn == "; ".join(concept.label for concept in two_purposes)

    @pytest.mark.parametrize(
        "text",
        ["Onshore (continental)", "onshore (continental)", "onshore_continental"],
    )
    def test_a_label_or_a_key_is_accepted_in_any_case(self, environment, text):
        assert environment.clean(text) == "onshore_continental"

    def test_several_terms_are_accepted_by_label_or_key(self, purposes, two_purposes):
        text = f"{two_purposes[0].label.upper()}; {two_purposes[1].name}"

        cleaned = purposes.clean(text)

        assert set(cleaned) == set(two_purposes)

    def test_an_unknown_term_is_refused_and_named(self, environment):
        with pytest.raises(ValidationError) as refusal:
            environment.clean("swamp")

        assert refusal.value.code == "unknown_term"
        assert "swamp" in str(refusal.value)

    def test_one_unknown_term_among_several_is_refused(self, purposes, two_purposes):
        with pytest.raises(ValidationError) as refusal:
            purposes.clean(f"{two_purposes[0].label}; swamp")

        assert refusal.value.code == "unknown_term"

    def test_untouched_text_returns_the_stored_term_the_vocabulary_no_longer_offers(
        self, environment
    ):
        environment.stored = "withdrawn_term"

        assert environment.clean(environment.prepare_value("withdrawn_term")) == (
            "withdrawn_term"
        )

    def test_untouched_text_returns_the_stored_terms(self, purposes, two_purposes):
        purposes.stored = two_purposes

        assert purposes.clean(purposes.prepare_value(two_purposes)) == two_purposes

    def test_an_empty_optional_field_stores_no_term(self, db):
        from heat_flow.forms import ConceptTextField
        from heat_flow.models import HeatFlowSite

        single = ConceptTextField(
            HeatFlowSite._meta.get_field("environment"), required=False
        )
        several = ConceptTextField(
            HeatFlowSite._meta.get_field("explo_purpose"), required=False
        )

        assert single.clean("") is None
        assert several.clean("").count() == 0


class TestHeatFlowFormfield:
    def test_a_vocabulary_field_is_drawn_as_text(self):
        from heat_flow.forms import ConceptTextField, heat_flow_formfield
        from heat_flow.models import HeatFlowSite

        for name in ("environment", "explo_purpose"):
            field = heat_flow_formfield(HeatFlowSite._meta.get_field(name))

            assert isinstance(field, ConceptTextField)

    def test_any_other_multiple_choice_is_a_counted_tom_select(self):
        from heat_flow.forms import heat_flow_formfield
        from heat_flow.models import HeatFlowSite
        from mvp_forms.widgets import TomSelectMultiple

        field = heat_flow_formfield(HeatFlowSite._meta.get_field("stratigraphy"))

        assert isinstance(field.widget, TomSelectMultiple)
        assert field.widget.counted is True

    def test_a_plain_field_is_left_as_the_model_draws_it(self):
        from django import forms
        from heat_flow.forms import heat_flow_formfield
        from heat_flow.models import HeatFlowSite

        field = heat_flow_formfield(HeatFlowSite._meta.get_field("country"))

        assert isinstance(field, forms.CharField)
