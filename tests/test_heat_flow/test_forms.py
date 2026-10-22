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


FORM_NAMES = [
    "HeatFlowSiteForm",
    "HeatFlowIntervalForm",
    "HeatFlowForm",
    "ThermalGradientForm",
    "IntervalConductivityForm",
    "ParentHeatFlowForm",
]


def drawn_names(form):
    """Name every field the form's layout draws, in order."""
    return [pointer.name for pointer in form.helper.layout.get_field_names()]


class TestSectionedForm:
    @pytest.mark.parametrize("name", FORM_NAMES)
    def test_every_field_is_placed_exactly_once(self, name):
        from heat_flow import forms

        form = getattr(forms, name)()

        assert sorted(drawn_names(form)) == sorted(form.fields)

    def test_a_field_named_in_no_section_is_still_placed(self):
        from heat_flow.forms import ThermalGradientForm

        class Partial(ThermalGradientForm):
            sections = ((None, ["value"]),)
            measured_pairs = ()

        form = Partial()

        assert sorted(drawn_names(form)) == sorted(form.fields)

    def test_the_first_group_has_no_heading_and_later_groups_are_panels(self):
        from heat_flow.forms import HeatFlowSiteForm
        from mvp_forms.layout import Fieldset

        drawn = HeatFlowSiteForm().helper.layout.fields

        assert not isinstance(drawn[0], Fieldset)
        assert len(drawn) > 1
        assert all(isinstance(group, Fieldset) for group in drawn[1:])

    def test_a_measured_pair_is_two_numbers_and_a_unit_drawn_as_one_join(self):
        from django import forms
        from heat_flow.forms import ThermalGradientForm
        from mvp_forms.layout import Join

        form = ThermalGradientForm()
        join = form.helper.layout.fields[0]
        members = [
            pointer.name
            for pointer in form.helper.layout.get_field_names()
            if pointer.positions[:-1] == [0]
        ]

        assert isinstance(join, Join)
        assert members == ["value", "uncertainty", "value_unit"]
        assert isinstance(form.fields["value"], forms.DecimalField)
        assert isinstance(form.fields["uncertainty"], forms.DecimalField)
        assert isinstance(form.fields["value_unit"], forms.ChoiceField)

    def test_numbers_in_another_unit_are_stored_in_base_units(self, db, monkeypatch):
        from decimal import Decimal

        from heat_flow.forms import ThermalGradientForm
        from heat_flow.models import ThermalGradient

        field = ThermalGradient._meta.get_field("value")
        monkeypatch.setattr(field, "unit_choices", ["K/km", "K/m"])
        form = ThermalGradientForm(
            data={"value": "0.0255", "uncertainty": "0.0012", "value_unit": "K/m"}
        )

        form.full_clean()

        assert form.cleaned_data["value"].magnitude == Decimal("25.50")
        assert form.cleaned_data["value"].units == field.base_units
        assert form.cleaned_data["uncertainty"].magnitude == Decimal("1.20")

    def test_numbers_beyond_the_fields_places_are_rounded_to_them(self, db):
        from decimal import Decimal

        from heat_flow.forms import ThermalGradientForm

        form = ThermalGradientForm(
            data={"value": "25.554", "uncertainty": "1.251", "value_unit": "K/km"}
        )

        form.full_clean()

        assert form.cleaned_data["value"].magnitude == Decimal("25.55")
        assert form.cleaned_data["uncertainty"].magnitude == Decimal("1.25")

    def test_numbers_in_the_base_unit_are_stored_as_entered(self, db):
        from decimal import Decimal

        from heat_flow.forms import ThermalGradientForm

        form = ThermalGradientForm(
            data={"value": "25.5", "uncertainty": "1.25", "value_unit": "K/km"}
        )

        form.full_clean()

        assert form.cleaned_data["value"].magnitude == Decimal("25.5")
        assert form.cleaned_data["uncertainty"].magnitude == Decimal("1.25")

    def test_floating_point_numbers_in_another_unit_are_converted(self, monkeypatch):
        from heat_flow.forms import ParentHeatFlowForm
        from heat_flow.models import ParentHeatFlow

        field = ParentHeatFlow._meta.get_field("value")
        monkeypatch.setattr(field, "unit_choices", ["mW / m^2", "W / m^2"])
        form = ParentHeatFlowForm(
            data={"value": "0.07", "uncertainty": "0.005", "value_unit": "W / m^2"}
        )

        form.full_clean()

        assert form.cleaned_data["value"].magnitude == pytest.approx(70)
        assert form.cleaned_data["uncertainty"].magnitude == pytest.approx(5)

    def test_the_initial_numbers_are_the_stored_quantities_in_base_units(self):
        from decimal import Decimal

        from heat_flow.forms import ThermalGradientForm
        from heat_flow.models import ThermalGradient
        from quantityfield.units import ureg

        stored = ThermalGradient(
            value=ureg.Quantity(Decimal("0.0255"), "K/m"),
            uncertainty=ureg.Quantity(Decimal("1.25"), "K/km"),
        )

        form = ThermalGradientForm(instance=stored)

        assert float(form.initial["value"]) == pytest.approx(25.5)
        assert float(form.initial["uncertainty"]) == pytest.approx(1.25)
        assert form.initial["value_unit"] == "K/km"
