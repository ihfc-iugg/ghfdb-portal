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

    @pytest.fixture
    def stored_site(self, db, two_purposes):
        from tests.factories import HeatFlowSiteFactory

        return HeatFlowSiteFactory(
            environment="onshore_continental", explo_purpose=two_purposes
        )

    def test_an_unbound_form_draws_a_stored_term_as_its_label(self, stored_site):
        from heat_flow.forms import HeatFlowSiteForm
        from heat_flow.vocabularies import GeographicEnvironment

        label = dict(GeographicEnvironment().choices)["onshore_continental"]

        form = HeatFlowSiteForm(instance=stored_site)

        assert form["environment"].value() == label

    def test_an_unbound_form_draws_several_stored_terms_joined_by_semicolons(
        self, stored_site, two_purposes
    ):
        from heat_flow.forms import HeatFlowSiteForm

        form = HeatFlowSiteForm(instance=stored_site)

        assert form["explo_purpose"].value() == "; ".join(
            concept.label for concept in stored_site.explo_purpose.all()
        )

    def test_a_bound_form_redraws_posted_text_unchanged(self, stored_site):
        from heat_flow.forms import HeatFlowSiteForm

        form = HeatFlowSiteForm(
            instance=stored_site,
            data=site_data(stored_site, environment="swamp", explo_purpose="a; b"),
        )

        assert form["environment"].value() == "swamp"
        assert form["explo_purpose"].value() == "a; b"

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

        assert environment.clean(environment.as_text("withdrawn_term")) == (
            "withdrawn_term"
        )

    def test_untouched_text_returns_the_stored_terms(self, purposes, two_purposes):
        purposes.stored = two_purposes

        assert purposes.clean(purposes.as_text(two_purposes)) == two_purposes

    def test_the_label_stays_translatable_and_keeps_a_capital_after_a_lowercase_first(
        self,
    ):
        from django.utils.functional import Promise
        from heat_flow.forms import ConceptTextField
        from heat_flow.models import IntervalConductivity

        field = ConceptTextField(IntervalConductivity._meta.get_field("pT_conditions"))

        assert isinstance(field.label, Promise)
        assert str(field.label)[:2] == "PT"

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

    def test_a_plain_field_is_left_as_the_model_draws_it(self):
        from heat_flow.forms import heat_flow_formfield
        from heat_flow.models import HeatFlowSite

        db_field = HeatFlowSite._meta.get_field("country")

        field = heat_flow_formfield(db_field)

        drawn = db_field.formfield()
        assert type(field) is type(drawn)
        assert type(field.widget) is type(drawn.widget)


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

    def test_a_measured_pair_is_two_numbers_and_a_unit(self):
        from django import forms
        from heat_flow.forms import ThermalGradientForm

        fields = ThermalGradientForm().fields

        assert {"value", "uncertainty", "value_unit"} <= set(fields)
        assert isinstance(fields["value"], forms.DecimalField)
        assert isinstance(fields["uncertainty"], forms.DecimalField)
        assert isinstance(fields["value_unit"], forms.ChoiceField)

    def test_a_measured_number_keeps_its_translatable_label(self):
        from django.utils.functional import Promise
        from heat_flow.forms import ThermalGradientForm

        form = ThermalGradientForm()

        assert isinstance(form.fields["value"].label, Promise)
        assert isinstance(form.fields["corrected_value"].label, Promise)

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

    def test_too_many_places_in_the_base_unit_are_refused_against_the_field(self, db):
        from heat_flow.forms import ThermalGradientForm
        from heat_flow.models import ThermalGradient

        form = ThermalGradientForm(
            data={"value": "25.554", "uncertainty": "1.25", "value_unit": "K/km"}
        )

        assert not form.is_valid()
        assert form.has_error("value", code="max_decimal_places")
        assert not form.has_error("uncertainty")
        assert not ThermalGradient.objects.exists()

    def test_a_value_converted_from_another_unit_is_quantised_to_the_places(
        self, db, monkeypatch
    ):
        from decimal import Decimal

        from heat_flow.forms import ThermalGradientForm
        from heat_flow.models import ThermalGradient

        field = ThermalGradient._meta.get_field("value")
        monkeypatch.setattr(field, "unit_choices", ["K/km", "K/m"])
        form = ThermalGradientForm(
            data={"value": "0.025554", "uncertainty": "0.001251", "value_unit": "K/m"}
        )

        form.full_clean()

        assert not form.has_error("value")
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


def site_data(site, **changes):
    """Post the data a researcher's browser sends for a site, with these changes."""
    data = {
        "name": site.name,
        "location_first": str(site.location.y),
        "location_second": str(site.location.x),
        "elevation_datum": "MSL",
        "environment": "Onshore (continental)",
        "explo_method": "",
        "explo_purpose": "",
    }
    return {**data, **changes}


class TestHeatFlowSiteForm:
    @pytest.fixture
    def site(self, db):
        from tests.factories import HeatFlowSiteFactory

        return HeatFlowSiteFactory(name="Original")

    def test_it_offers_every_mapped_site_column(self):
        from heat_flow.forms import HeatFlowSiteForm

        from tests.test_docs.test_field_map import read_mappings

        mapped = {
            mapping.accessor.split(" ")[0]
            for mapping in read_mappings()
            if mapping.accessed_from == "HeatFlowSite"
        }

        assert mapped <= set(HeatFlowSiteForm().fields)

    def test_it_offers_nothing_the_portal_calculates_or_assigns(self):
        from heat_flow.forms import HeatFlowSiteForm

        withheld = {
            "U_score",
            "M_score",
            "T_score",
            "TC_score",
            "quality",
            "quality_scheme",
            "ghfdb_id",
            "dataset",
            "sample",
        }

        assert not withheld & set(HeatFlowSiteForm().fields)

    def test_the_location_takes_a_latitude_and_a_longitude_only(self):
        from heat_flow.forms import HeatFlowSiteForm

        location = HeatFlowSiteForm().fields["location"]

        assert len(location.fields) == 2

    def test_elevation_and_datum_are_saved_on_the_site_itself(self, site):
        from heat_flow.forms import HeatFlowSiteForm

        form = HeatFlowSiteForm(
            instance=site,
            data=site_data(
                site, elevation_0="350", elevation_1="m", elevation_datum="NAVD88"
            ),
        )

        assert form.is_valid(), form.errors
        form.save()
        site.refresh_from_db()
        assert site.elevation.m_as("m") == 350
        assert str(site.elevation_datum) == "NAVD88"
        assert site.location_elevation is None

    def test_a_changed_vertical_depth_is_stored_on_a_site_with_a_bottom(self, site):
        from heat_flow.forms import HeatFlowSiteForm

        site.vertical_depth = 500
        site.save()
        site.refresh_from_db()
        assert site.bottom.m_as("m") == 500
        form = HeatFlowSiteForm(
            instance=site,
            data=site_data(site, vertical_depth_0="800", vertical_depth_1="m"),
        )

        assert form.is_valid(), form.errors
        form.save()
        site.refresh_from_db()
        assert site.vertical_depth.m_as("m") == 800

    def test_a_location_held_by_another_site_is_refused_and_nothing_is_written(
        self, site
    ):
        from heat_flow.forms import HeatFlowSiteForm
        from heat_flow.models import HeatFlowSite

        from tests.factories import HeatFlowSiteFactory

        other = HeatFlowSiteFactory()
        form = HeatFlowSiteForm(
            instance=site,
            data=site_data(
                site,
                name="Renamed",
                location_first=str(other.location.y),
                location_second=str(other.location.x),
            ),
        )

        assert not form.is_valid()
        assert form.has_error("location", code="duplicate_location")
        stored = HeatFlowSite.objects.get(pk=site.pk)
        assert stored.name == "Original"
        assert stored.location != other.location

    def test_a_site_may_keep_its_own_location(self, site):
        from heat_flow.forms import HeatFlowSiteForm

        form = HeatFlowSiteForm(instance=site, data=site_data(site))

        assert form.is_valid(), form.errors

    @pytest.mark.parametrize("name", ["environment", "explo_method", "explo_purpose"])
    def test_a_term_outside_the_vocabulary_is_refused(self, site, name):
        from heat_flow.forms import HeatFlowSiteForm

        form = HeatFlowSiteForm(
            instance=site, data=site_data(site, **{name: "not a term"})
        )

        assert form.has_error(name, code="unknown_term")

    def test_an_environment_the_vocabulary_holds_as_unspecified_is_saved(self, site):
        from heat_flow.forms import HeatFlowSiteForm

        form = HeatFlowSiteForm(
            instance=site, data=site_data(site, environment="Unspecified")
        )
        assert form.is_valid(), form.errors

        form.save()

        site.refresh_from_db()
        assert site.environment.name == "unspecified"

    def test_the_exploration_purpose_takes_several_terms(self, site):
        from heat_flow.forms import HeatFlowSiteForm
        from heat_flow.vocabularies import ExplorationPurpose
        from research_vocabs.models import Concept

        chosen = list(
            Concept.get_for_vocabulary(ExplorationPurpose).order_by("name")[:2]
        )
        text = "; ".join(concept.label for concept in chosen)
        form = HeatFlowSiteForm(instance=site, data=site_data(site, explo_purpose=text))

        assert form.is_valid(), form.errors
        form.save()
        assert set(site.explo_purpose.all()) == set(chosen)


@pytest.fixture
def researcher(client):
    """Return a function that signs in a researcher with no team role who owns a dataset."""

    def sign_in(dataset):
        from fairdm.contrib.contributors.choices import ContributionLevel
        from fairdm.factories import UserFactory

        user = UserFactory()
        credit = dataset.add_contributor(user)
        credit.level = ContributionLevel.MANAGE
        credit.save()
        client.force_login(user)
        return client

    return sign_in


class TestHeatFlowSiteEditPage:
    def edit_url(self, site):
        from fairdm.contrib.plugins import reverse

        return reverse(site, "edit")

    def test_a_dataset_owner_corrects_the_elevation_datum_and_vertical_depth(
        self, db, researcher
    ):
        from fairdm.factories import DatasetFactory
        from fairdm.utils.choices import Visibility

        from tests.factories import HeatFlowSiteFactory

        dataset = DatasetFactory(visibility=Visibility.PUBLIC, published=True)
        site = HeatFlowSiteFactory(dataset=dataset, name="Original")
        client = researcher(dataset)

        response = client.post(
            self.edit_url(site),
            site_data(
                site,
                elevation_0="350",
                elevation_1="m",
                elevation_datum="NAVD88",
                vertical_depth_0="800",
                vertical_depth_1="m",
            ),
        )

        assert response.status_code == 302
        site.refresh_from_db()
        assert site.elevation.m_as("m") == 350
        assert str(site.elevation_datum) == "NAVD88"
        assert site.vertical_depth.m_as("m") == 800

    def test_a_save_shows_a_site_awaiting_review_to_no_one_new(self, db, researcher):
        from django.test import Client
        from fairdm.factories import DatasetFactory, UserFactory
        from fairdm.utils.choices import Visibility

        from tests.factories import HeatFlowSiteFactory

        dataset = DatasetFactory(visibility=Visibility.PUBLIC, published=False)
        site = HeatFlowSiteFactory(dataset=dataset)
        stranger = Client()
        stranger.force_login(UserFactory())
        anonymous = Client()
        before = [
            visitor.get(site.get_absolute_url()).status_code
            for visitor in (anonymous, stranger)
        ]
        owner = researcher(dataset)

        response = owner.post(
            self.edit_url(site),
            site_data(site, elevation_0="12", elevation_1="m"),
        )

        assert response.status_code == 302
        after = [
            visitor.get(site.get_absolute_url()).status_code
            for visitor in (anonymous, stranger)
        ]
        assert before == after
        assert 200 not in after


def interval_data(interval, **changes):
    """Post the data a researcher's browser sends for an interval, with these changes."""
    data = {
        "top_0": "0",
        "top_1": "m",
        "bottom_0": "500",
        "bottom_1": "m",
        "vertical_datum": interval.vertical_datum,
        "lithology": "",
        "age": "",
    }
    return {**data, **changes}


class TestHeatFlowIntervalForm:
    @pytest.fixture
    def interval(self, db):
        from tests.factories import HeatFlowIntervalFactory

        return HeatFlowIntervalFactory(top=0, bottom=500)

    def build(self, interval, **changes):
        from heat_flow.forms import HeatFlowIntervalForm

        return HeatFlowIntervalForm(
            instance=interval, data=interval_data(interval, **changes)
        )

    def test_it_offers_every_mapped_interval_and_probe_column(self):
        from heat_flow.forms import HeatFlowIntervalForm

        from tests.test_docs.test_field_map import read_mappings

        mappings = read_mappings()
        interval = {
            mapping.accessor.split(" ")[0]
            for mapping in mappings
            if mapping.accessed_from == "HeatFlowInterval"
        } - {"identifiers"}
        probe = {
            mapping.column
            for mapping in mappings
            if mapping.accessed_from == "ProbeMetadata"
        }

        assert interval | probe <= set(HeatFlowIntervalForm().fields)
        assert "identifiers" not in HeatFlowIntervalForm().fields

    def test_it_offers_nothing_the_portal_calculates_or_assigns(self):
        from heat_flow.forms import HeatFlowIntervalForm

        withheld = {
            "U_score",
            "M_score",
            "T_score",
            "TC_score",
            "quality",
            "quality_scheme",
            "ghfdb_id",
            "dataset",
            "sample",
        }

        assert not withheld & set(HeatFlowIntervalForm().fields)

    def test_an_interval_with_no_probe_entered_gains_none(self, interval):
        from heat_flow.models.child import ProbeMetadata

        form = self.build(interval, bottom_0="600")
        assert form.is_valid(), form.errors

        form.save()

        assert not ProbeMetadata.objects.filter(interval=interval).exists()

    def test_a_probe_type_and_a_tilt_create_the_probe_metadata(self, interval):
        form = self.build(
            interval,
            probe_type="Violin-Bow probe (Lister)",
            probe_tilt_0="12.5",
            probe_tilt_1="°",
        )
        assert form.is_valid(), form.errors

        form.save()

        probe = interval.probe_metadata
        assert [concept.name for concept in probe.probe_type.all()] == ["violin_bow"]
        assert probe.tilt.m_as("°") == pytest.approx(12.5)
        assert probe.penetration is None
        assert probe.length is None

    def test_a_tilt_of_zero_creates_the_probe_metadata(self, interval):
        form = self.build(interval, probe_tilt_0="0", probe_tilt_1="°")
        assert form.is_valid(), form.errors

        form.save()

        probe = interval.probe_metadata
        assert probe.tilt is not None
        assert probe.tilt.m_as("°") == 0
        assert not probe.probe_type.exists()

    def test_the_stored_probe_values_are_the_initial_values_and_an_edit_updates_the_row(
        self, interval
    ):
        from heat_flow.forms import HeatFlowIntervalForm
        from heat_flow.models.child import ProbeMetadata

        from tests.factories import ProbeMetadataFactory

        stored = ProbeMetadataFactory(
            interval=interval, penetration=3, length=4, tilt=5
        )
        fresh = type(interval).objects.get(pk=interval.pk)
        fields = HeatFlowIntervalForm(instance=fresh).fields

        assert fields["probe_penetration"].initial.m_as("m") == 3
        assert fields["probe_length"].initial.m_as("m") == 4
        assert fields["probe_tilt"].initial.m_as("°") == 5
        form = self.build(
            interval,
            probe_penetration_0="7",
            probe_penetration_1="m",
            probe_length_0="4",
            probe_length_1="m",
            probe_tilt_0="9",
            probe_tilt_1="°",
        )
        assert form.is_valid(), form.errors

        form.save()

        assert ProbeMetadata.objects.filter(interval=interval).count() == 1
        stored.refresh_from_db()
        assert stored.penetration.m_as("m") == 7
        assert stored.tilt.m_as("°") == 9
        assert not stored.probe_type.exists()

    @pytest.mark.parametrize(
        "changes, name",
        [
            ({"probe_tilt_0": "95", "probe_tilt_1": "°"}, "probe_tilt"),
            (
                {"probe_penetration_0": "-5", "probe_penetration_1": "m"},
                "probe_penetration",
            ),
        ],
    )
    def test_a_probe_value_out_of_range_is_refused_against_its_field(
        self, interval, changes, name
    ):
        from heat_flow.models.child import ProbeMetadata

        form = self.build(interval, **changes)

        assert not form.is_valid()
        assert form.errors.keys() == {name}
        assert not ProbeMetadata.objects.exists()

    def test_a_stored_probe_is_checked_with_the_values_entered(self, interval):
        from tests.factories import ProbeMetadataFactory

        stored = ProbeMetadataFactory(interval=interval, tilt=5)
        form = self.build(interval, probe_tilt_0="95", probe_tilt_1="°")

        assert not form.is_valid()
        assert form.has_error("probe_tilt")
        stored.refresh_from_db()
        assert stored.tilt.m_as("°") == 5

    def test_a_bottom_not_below_the_top_is_refused_and_nothing_is_written(
        self, interval
    ):
        from heat_flow.models.child import ProbeMetadata

        form = self.build(
            interval,
            top_0="600",
            bottom_0="100",
            probe_tilt_0="12",
            probe_tilt_1="°",
        )

        assert not form.is_valid()
        assert form.non_field_errors()
        interval.refresh_from_db()
        assert interval.top.m_as("m") == 0
        assert interval.bottom.m_as("m") == 500
        assert not ProbeMetadata.objects.exists()

    def test_saving_without_commit_then_saving_m2m_writes_the_probe_metadata(
        self, interval
    ):
        from heat_flow.models.child import ProbeMetadata

        form = self.build(interval, probe_tilt_0="12", probe_tilt_1="°")
        assert form.is_valid(), form.errors

        saved = form.save(commit=False)

        assert not ProbeMetadata.objects.exists()
        saved.save()
        form.save_m2m()
        assert saved.probe_metadata.tilt.m_as("°") == 12


class TestHeatFlowIntervalEditPage:
    def test_a_dataset_owner_enters_a_probe_type_and_a_tilt(self, db, researcher):
        from fairdm.contrib.plugins import reverse
        from fairdm.factories import DatasetFactory
        from fairdm.utils.choices import Visibility

        from tests.factories import HeatFlowIntervalFactory

        dataset = DatasetFactory(visibility=Visibility.PUBLIC, published=True)
        interval = HeatFlowIntervalFactory(dataset=dataset, top=0, bottom=500)
        client = researcher(dataset)

        response = client.post(
            reverse(interval, "edit"),
            interval_data(
                interval,
                probe_type="Violin-Bow probe (Lister)",
                probe_tilt_0="12.5",
                probe_tilt_1="°",
            ),
        )

        assert response.status_code == 302
        probe = interval.probe_metadata
        assert [concept.name for concept in probe.probe_type.all()] == ["violin_bow"]
        assert probe.tilt.m_as("°") == pytest.approx(12.5)


@pytest.fixture
def editor(db):
    """Return a function that makes a request for a researcher who owns a dataset."""

    def build(dataset):
        from django.test import RequestFactory
        from fairdm.contrib.contributors.choices import ContributionLevel
        from fairdm.factories import UserFactory

        user = UserFactory()
        credit = dataset.add_contributor(user)
        credit.level = ContributionLevel.MANAGE
        credit.save()
        request = RequestFactory().get("/")
        request.user = user
        return request

    return build


@pytest.fixture
def child_records(db):
    """A child on an interval with a gradient and a conductivity of its own."""
    from fairdm.factories import DatasetFactory
    from fairdm.utils.choices import Visibility

    from tests.factories import (
        HeatFlowFactory,
        HeatFlowIntervalFactory,
        IntervalConductivityFactory,
        ThermalGradientFactory,
    )

    dataset = DatasetFactory(visibility=Visibility.PUBLIC, published=True)
    interval = HeatFlowIntervalFactory(dataset=dataset, top=0, bottom=500)
    gradient = ThermalGradientFactory(dataset=dataset, sample=interval)
    conductivity = IntervalConductivityFactory(dataset=dataset, sample=interval)
    child = HeatFlowFactory(
        dataset=dataset,
        sample=interval,
        ghfdb_id=1000,
        value=70,
        uncertainty=5,
        thermal_gradient=gradient,
        thermal_conductivity=conductivity,
    )
    child.refresh_from_db()
    return {
        "dataset": dataset,
        "interval": interval,
        "gradient": gradient,
        "conductivity": conductivity,
        "child": child,
    }


def child_data(child, **changes):
    """Post the data a researcher's browser sends for a child, with these changes."""
    data = {
        "value": "70",
        "uncertainty": "5",
        "value_unit": "mW / m^2",
        "method": "",
        "thermal_gradient": str(child.thermal_gradient_id or ""),
        "thermal_conductivity": str(child.thermal_conductivity_id or ""),
    }
    return {**data, **changes}


CORRECTION_CODES = ["IS", "T", "S", "E", "TOPO", "PAL", "SUR", "CONV", "HR"]


class TestHeatFlowForm:
    def build(self, records, editor, **changes):
        from heat_flow.forms import HeatFlowForm

        return HeatFlowForm(
            instance=records["child"],
            data=child_data(records["child"], **changes),
            request=editor(records["dataset"]),
        )

    def test_it_offers_every_mapped_child_column_and_each_correction(self):
        import re

        from heat_flow.forms import HeatFlowForm

        from tests.test_docs.test_field_map import read_mappings

        mappings = read_mappings()
        mapped = {
            mapping.accessor.split(" ")[0]
            for mapping in mappings
            if mapping.accessed_from == "HeatFlow"
        } - {"ghfdb_id", "quality", "is_relevant"}
        corrections = {
            f"correction_{re.search(r'type=(\w+)', mapping.accessor).group(1)}"
            for mapping in mappings
            if mapping.accessed_from == "HeatFlowCorrection"
        }

        assert mapped | corrections <= set(HeatFlowForm().fields)
        assert len(corrections) == 9

    def test_it_offers_nothing_the_portal_calculates_or_assigns(self):
        from heat_flow.forms import HeatFlowForm

        withheld = {
            "U_score",
            "M_score",
            "T_score",
            "TC_score",
            "T_score_missing",
            "TC_score_missing",
            "quality",
            "quality_scheme",
            "ghfdb_id",
            "dataset",
            "sample",
            "is_relevant",
        }

        assert not withheld & set(HeatFlowForm().fields)

    @pytest.mark.parametrize("code", CORRECTION_CODES)
    def test_each_correction_offers_an_empty_entry_and_the_statuses_valid_for_it(
        self, code
    ):
        from heat_flow.forms import HeatFlowForm
        from heat_flow.models import HeatFlowCorrection

        valid = HeatFlowCorrection.VALID_STATUS_FOR_TYPE.get(
            code, HeatFlowCorrection.ENVIRONMENTAL_VALID
        )

        offered = [
            value
            for value, _label in HeatFlowForm().fields[f"correction_{code}"].choices
        ]

        assert offered[0] == ""
        assert set(offered[1:]) == valid
        assert "-" not in offered

    def test_a_gradient_and_a_conductivity_on_the_childs_interval_save(
        self, child_records, editor
    ):
        from tests.factories import IntervalConductivityFactory, ThermalGradientFactory

        other_gradient = ThermalGradientFactory(
            dataset=child_records["dataset"], sample=child_records["interval"]
        )
        other_conductivity = IntervalConductivityFactory(
            dataset=child_records["dataset"], sample=child_records["interval"]
        )
        form = self.build(
            child_records,
            editor,
            thermal_gradient=str(other_gradient.pk),
            thermal_conductivity=str(other_conductivity.pk),
        )

        assert form.is_valid(), form.errors
        child = form.save()
        child.refresh_from_db()
        assert child.thermal_gradient == other_gradient
        assert child.thermal_conductivity == other_conductivity

    @pytest.mark.parametrize(
        ("field", "factory_name"),
        [
            ("thermal_gradient", "ThermalGradientFactory"),
            ("thermal_conductivity", "IntervalConductivityFactory"),
        ],
    )
    def test_a_measurement_on_another_interval_is_refused_and_nothing_is_written(
        self, child_records, editor, field, factory_name
    ):
        from tests import factories
        from tests.factories import HeatFlowIntervalFactory

        elsewhere = HeatFlowIntervalFactory(dataset=child_records["dataset"])
        foreign = getattr(factories, factory_name)(
            dataset=child_records["dataset"], sample=elsewhere
        )
        child = child_records["child"]
        before = getattr(child, f"{field}_id")
        form = self.build(
            child_records,
            editor,
            **{field: str(foreign.pk), "correction_TOPO": "present_corrected"},
        )

        assert not form.is_valid()
        assert form.has_error(field, code="other_interval")
        child.refresh_from_db()
        assert getattr(child, f"{field}_id") == before
        assert not child.corrections.exists()

    def test_a_gradient_in_a_dataset_the_researcher_may_not_change_is_refused(
        self, child_records, editor
    ):
        from fairdm.factories import DatasetFactory
        from fairdm.utils.choices import Visibility

        from tests.factories import ThermalGradientFactory

        locked = DatasetFactory(visibility=Visibility.PUBLIC, published=True)
        foreign = ThermalGradientFactory(
            dataset=locked, sample=child_records["interval"]
        )
        child = child_records["child"]
        before = child.thermal_gradient_id
        form = self.build(child_records, editor, thermal_gradient=str(foreign.pk))

        assert not form.is_valid()
        assert form.has_error("thermal_gradient")
        assert not form.has_error("thermal_gradient", code="other_interval")
        child.refresh_from_db()
        assert child.thermal_gradient_id == before

    def test_setting_one_correction_on_a_child_with_no_rows_leaves_nine_rows(
        self, child_records, editor
    ):
        child = child_records["child"]
        assert not child.corrections.exists()
        form = self.build(child_records, editor, correction_TOPO="present_corrected")

        assert form.is_valid(), form.errors
        form.save()

        statuses = {c.correction_type: c.status for c in child.corrections.all()}
        assert len(statuses) == 9
        assert statuses.pop("TOPO") == "present_corrected"
        assert set(statuses.values()) == {""}

    def test_clearing_a_correction_stores_an_empty_status_and_keeps_its_comment(
        self, child_records, editor
    ):
        from tests.factories import HeatFlowCorrectionFactory

        child = child_records["child"]
        HeatFlowCorrectionFactory(
            heat_flow=child,
            correction_type="SUR",
            status="present_corrected",
            comment="Bottom water measured.",
        )
        form = self.build(child_records, editor, correction_SUR="")

        assert form.is_valid(), form.errors
        form.save()

        correction = child.corrections.get(correction_type="SUR")
        assert correction.status == ""
        assert correction.comment == "Bottom water measured."

    def test_the_stored_statuses_are_the_initial_choices(self, child_records, editor):
        from heat_flow.forms import HeatFlowForm

        from tests.factories import HeatFlowCorrectionFactory

        HeatFlowCorrectionFactory(
            heat_flow=child_records["child"],
            correction_type="E",
            status="not_recognized",
        )

        form = HeatFlowForm(instance=child_records["child"])

        assert form["correction_E"].value() == "not_recognized"
        assert form["correction_IS"].value() in ("", None)

    def test_the_method_takes_several_method_terms(self, child_records, editor):
        from heat_flow.vocabularies import HeatFlowMethod
        from research_vocabs.models import Concept

        chosen = list(Concept.get_for_vocabulary(HeatFlowMethod).order_by("name")[:2])
        text = "; ".join(concept.label for concept in chosen)
        form = self.build(child_records, editor, method=text)

        assert form.is_valid(), form.errors
        child = form.save()
        assert set(child.method.all()) == set(chosen)

    def test_a_method_outside_its_vocabulary_is_refused(self, child_records, editor):
        form = self.build(child_records, editor, method="not a method")

        assert form.has_error("method", code="unknown_term")

    def test_saving_without_commit_then_saving_m2m_writes_the_corrections(
        self, child_records, editor
    ):
        child = child_records["child"]
        form = self.build(child_records, editor, correction_PAL="considered_t")
        assert form.is_valid(), form.errors

        saved = form.save(commit=False)

        assert not child.corrections.exists()
        saved.save()
        form.save_m2m()
        assert child.corrections.count() == 9
        assert child.corrections.get(correction_type="PAL").status == "considered_t"


class TestHeatFlowEditPage:
    def edit_url(self, child):
        from fairdm.contrib.plugins import reverse

        return reverse(child, "edit")

    @pytest.fixture
    def corrected(self, child_records, researcher):
        """Post the child's edit page: another gradient, topography present and corrected."""
        from tests.factories import ThermalGradientFactory

        other = ThermalGradientFactory(
            dataset=child_records["dataset"], sample=child_records["interval"]
        )
        child = child_records["child"]
        child.refresh_from_db()
        before = child.quality.split(".")[2]
        client = researcher(child_records["dataset"])

        response = client.post(
            self.edit_url(child),
            child_data(
                child,
                thermal_gradient=str(other.pk),
                correction_TOPO="present_corrected",
            ),
        )

        assert response.status_code == 302
        child.refresh_from_db()
        return {**child_records, "gradient": other, "before": before}

    def test_a_dataset_owner_corrects_the_gradient_and_a_correction(self, corrected):
        child = corrected["child"]

        assert child.thermal_gradient == corrected["gradient"]
        assert child.corrections.count() == 9
        assert child.corrections.get(correction_type="TOPO").status == (
            "present_corrected"
        )

    def test_the_perturbation_flags_move_with_the_correction(self, corrected):
        assert corrected["before"] == "-------"
        assert corrected["child"].quality.split(".")[2] == "--T----"

    def test_the_exported_corrections_equal_those_of_an_import_of_the_same_values(
        self, corrected, db
    ):
        from fairdm.factories import DatasetFactory
        from heat_flow.models import HeatFlow

        from project.ghfdb.models import GHFDBChild
        from project.ghfdb.resources import (
            GHFDBChildImportResource,
            GHFDBParentImportResource,
        )
        from project.ghfdb.resources.export import GHFDBExportResource
        from tests.test_ghfdb.test_resources.test_child import (
            CHILD_ROW,
            PARENT_ROW,
            make_dataset,
        )

        imported_into = DatasetFactory()
        GHFDBParentImportResource().import_data(
            make_dataset(PARENT_ROW),
            dry_run=False,
            raise_errors=True,
            fairdm_dataset=imported_into,
        )
        row = {
            **CHILD_ROW,
            **{f"corr_{code}_flag": "" for code in CORRECTION_CODES},
            "corr_TOPO_flag": "present_corrected",
        }
        result = GHFDBChildImportResource().import_data(
            make_dataset(row),
            dry_run=False,
            raise_errors=False,
            fairdm_dataset=imported_into,
        )
        assert not result.has_errors(), result.invalid_rows
        imported = HeatFlow.objects.get(ghfdb_id=1)

        def corrections_of(child):
            queryset = GHFDBChild.objects.for_export().filter(pk=child.pk)
            exported = GHFDBExportResource().export(queryset).dict[0]
            return {
                code: exported[f"corr_{code.lower()}_flag"] for code in CORRECTION_CODES
            }

        assert corrections_of(corrected["child"]) == corrections_of(imported)
        assert corrections_of(corrected["child"])["TOPO"] == "present_corrected"
        assert corrections_of(corrected["child"])["IS"] == "-"


@pytest.fixture
def scored_records(db):
    """A borehole interval with a gradient, a conductivity, a child using both and a parent."""
    from fairdm.factories import DatasetFactory
    from fairdm.utils.choices import Visibility
    from heat_flow import vocabularies

    from tests.factories import (
        HeatFlowFactory,
        HeatFlowIntervalFactory,
        HeatFlowSiteFactory,
        IntervalConductivityFactory,
        ParentHeatFlowFactory,
        ThermalGradientFactory,
    )
    from tests.test_heat_flow.test_quality import concepts

    dataset = DatasetFactory(visibility=Visibility.PUBLIC, published=True)
    site = HeatFlowSiteFactory(dataset=dataset, explo_method="drilling")
    interval = HeatFlowIntervalFactory(dataset=dataset, site=site, top=0, bottom=1000)
    gradient = ThermalGradientFactory(
        dataset=dataset,
        sample=interval,
        number=10,
        method_top=concepts(vocabularies.TemperatureMethod, "LOGeq"),
        method_bottom=concepts(vocabularies.TemperatureMethod, "LOGeq"),
    )
    conductivity = IntervalConductivityFactory(
        dataset=dataset,
        sample=interval,
        number=30,
        source=concepts(vocabularies.ConductivitySource, "core_samples"),
        conductivity_location=concepts(vocabularies.ConductivityLocation, "actual"),
        saturation=concepts(vocabularies.ConductivitySaturation, "saturatedMeasured"),
        pT_conditions=concepts(vocabularies.ConductivityPTConditions, "actualInSitu"),
    )
    parent = ParentHeatFlowFactory(dataset=dataset, sample=site)
    child = HeatFlowFactory(
        dataset=dataset,
        sample=interval,
        thermal_gradient=gradient,
        thermal_conductivity=conductivity,
        parent=parent,
        is_relevant=True,
        value=70,
        uncertainty=7,
    )
    for record in (gradient, conductivity, child):
        record.refresh_from_db()
    return {
        "dataset": dataset,
        "interval": interval,
        "gradient": gradient,
        "conductivity": conductivity,
        "child": child,
    }


def gradient_data(**changes):
    """Post the data a researcher's browser sends for a gradient, with these changes."""
    data = {
        "value": "25.5",
        "value_unit": "K/km",
        "uncertainty": "1.25",
        "corrected_value": "26.5",
        "corrected_value_unit": "K/km",
        "corrected_uncertainty": "1.5",
        "method_top": "LOGeq",
        "method_bottom": "LOGeq",
        "correction_top": "",
        "correction_bottom": "",
        "number": "10",
    }
    return {**data, **changes}


class TestThermalGradientForm:
    def build(self, records, **changes):
        from heat_flow.forms import ThermalGradientForm

        return ThermalGradientForm(
            instance=records["gradient"], data=gradient_data(**changes)
        )

    def test_it_offers_every_mapped_gradient_column(self):
        from heat_flow.forms import ThermalGradientForm

        from tests.test_docs.test_field_map import read_mappings

        mapped = {
            mapping.accessor.split(" ")[0]
            for mapping in read_mappings()
            if mapping.accessed_from == "ThermalGradient"
        }

        assert len(mapped) == 11
        assert mapped <= set(ThermalGradientForm().fields)

    def test_it_offers_nothing_the_portal_calculates_or_assigns(self):
        from heat_flow.forms import ThermalGradientForm

        withheld = {"score", "score_missing", "quality_scheme", "dataset", "sample"}

        assert not withheld & set(ThermalGradientForm().fields)

    @pytest.mark.parametrize(
        "name", ["method_top", "method_bottom", "correction_top", "correction_bottom"]
    )
    def test_a_term_outside_the_vocabulary_is_refused_and_nothing_is_written(
        self, scored_records, name
    ):
        gradient = scored_records["gradient"]
        before = gradient.value
        form = self.build(scored_records, **{name: "not a term", "value": "30"})

        assert not form.is_valid()
        assert form.has_error(name, code="unknown_term")
        gradient.refresh_from_db()
        assert gradient.value == before

    def test_the_two_measured_pairs_convert_units_independently(
        self, scored_records, monkeypatch
    ):
        from decimal import Decimal

        from heat_flow.models import ThermalGradient

        for name in ("value", "corrected_value"):
            field = ThermalGradient._meta.get_field(name)
            monkeypatch.setattr(field, "unit_choices", ["K/km", "K/m"])
        form = self.build(
            scored_records,
            value="0.0255",
            value_unit="K/m",
            uncertainty="0.0012",
            corrected_value="26.5",
            corrected_value_unit="K/km",
            corrected_uncertainty="1.5",
        )

        assert form.is_valid(), form.errors
        gradient = form.save()
        gradient.refresh_from_db()
        assert gradient.value.m_as("K/km") == Decimal("25.50")
        assert gradient.uncertainty.m_as("K/km") == Decimal("1.20")
        assert gradient.corrected_value.m_as("K/km") == Decimal("26.50")
        assert gradient.corrected_uncertainty.m_as("K/km") == Decimal("1.50")

    def test_the_temperature_methods_take_several_terms(self, scored_records):
        from heat_flow import vocabularies

        from tests.test_heat_flow.test_quality import concepts

        form = self.build(scored_records, method_top="LOGeq; cLOG")

        assert form.is_valid(), form.errors
        gradient = form.save()
        assert set(gradient.method_top.all()) == set(
            concepts(vocabularies.TemperatureMethod, "LOGeq", "cLOG")
        )


def conductivity_data(**changes):
    """Post the data a researcher's browser sends for a conductivity, with these changes."""
    data = {
        "value": "2.5",
        "value_unit": "W/mK",
        "uncertainty": "0.25",
        "source": "core_samples",
        "conductivity_location": "actual",
        "method": "",
        "saturation": "saturatedMeasured",
        "pT_conditions": "actualInSitu",
        "pT_function": "",
        "number": "30",
        "strategy": "",
    }
    return {**data, **changes}


class TestIntervalConductivityForm:
    def build(self, records, **changes):
        from heat_flow.forms import IntervalConductivityForm

        return IntervalConductivityForm(
            instance=records["conductivity"], data=conductivity_data(**changes)
        )

    def test_it_offers_every_mapped_conductivity_column(self):
        from heat_flow.forms import IntervalConductivityForm

        from tests.test_docs.test_field_map import read_mappings

        mapped = {
            mapping.accessor.split(" ")[0]
            for mapping in read_mappings()
            if mapping.accessed_from == "IntervalConductivity"
        }

        assert len(mapped) == 10
        assert mapped <= set(IntervalConductivityForm().fields)

    def test_it_offers_nothing_the_portal_calculates_or_assigns(self):
        from heat_flow.forms import IntervalConductivityForm

        withheld = {"score", "score_missing", "quality_scheme", "dataset", "sample"}

        assert not withheld & set(IntervalConductivityForm().fields)

    @pytest.mark.parametrize(
        "name",
        [
            "source",
            "conductivity_location",
            "method",
            "saturation",
            "pT_conditions",
            "pT_function",
            "strategy",
        ],
    )
    def test_a_term_outside_the_vocabulary_is_refused_and_nothing_is_written(
        self, scored_records, name
    ):
        conductivity = scored_records["conductivity"]
        before = conductivity.value
        form = self.build(scored_records, **{name: "not a term", "value": "3"})

        assert not form.is_valid()
        assert form.has_error(name, code="unknown_term")
        conductivity.refresh_from_db()
        assert conductivity.value == before

    def test_the_source_takes_several_terms(self, scored_records):
        from heat_flow import vocabularies

        from tests.test_heat_flow.test_quality import concepts

        form = self.build(scored_records, source="core_samples; well_log")

        assert form.is_valid(), form.errors
        conductivity = form.save()
        assert set(conductivity.source.all()) == set(
            concepts(vocabularies.ConductivitySource, "core_samples", "well_log")
        )


class TestThermalGradientEditPage:
    def test_a_dataset_owner_corrects_the_scored_inputs_and_the_scores_move(
        self, scored_records, researcher
    ):
        from fairdm.contrib.plugins import reverse
        from heat_flow.models import HeatFlow

        gradient = scored_records["gradient"]
        child = scored_records["child"]
        assert gradient.score == pytest.approx(1.1)
        assert child.T_score == pytest.approx(1.1)
        client = researcher(scored_records["dataset"])

        response = client.post(
            reverse(gradient, "edit"),
            gradient_data(method_top="BHT", method_bottom="BHT", number="2"),
        )

        assert response.status_code == 302
        gradient.refresh_from_db()
        child = HeatFlow.objects.get(pk=child.pk)
        assert gradient.score == pytest.approx(0.7)
        assert child.T_score == pytest.approx(0.7)

    def test_a_refused_term_leaves_the_record_and_its_scores_as_they_were(
        self, scored_records, researcher
    ):
        from fairdm.contrib.plugins import reverse
        from heat_flow.models import HeatFlow

        gradient = scored_records["gradient"]
        client = researcher(scored_records["dataset"])

        response = client.post(
            reverse(gradient, "edit"),
            gradient_data(method_top="not a term", number="2"),
        )

        assert response.status_code == 200
        gradient.refresh_from_db()
        child = HeatFlow.objects.get(pk=scored_records["child"].pk)
        assert gradient.number == 10
        assert gradient.score == pytest.approx(1.1)
        assert child.T_score == pytest.approx(1.1)


class TestIntervalConductivityEditPage:
    def test_a_dataset_owner_corrects_the_location_and_number_and_the_scores_move(
        self, scored_records, researcher
    ):
        from fairdm.contrib.plugins import reverse
        from heat_flow.models import HeatFlow

        conductivity = scored_records["conductivity"]
        child = scored_records["child"]
        assert conductivity.score == pytest.approx(1.0)
        assert child.TC_score == pytest.approx(0.8)
        client = researcher(scored_records["dataset"])

        response = client.post(
            reverse(conductivity, "edit"),
            conductivity_data(conductivity_location="other", number="10"),
        )

        assert response.status_code == 302
        conductivity.refresh_from_db()
        child = HeatFlow.objects.get(pk=child.pk)
        assert conductivity.score == pytest.approx(0.8)
        assert child.TC_score == pytest.approx(0.6)


@pytest.fixture
def parent_records(db):
    """A site with a parent and three children; only the best-graded child is relevant."""
    from fairdm.factories import DatasetFactory
    from fairdm.utils.choices import Visibility

    from tests.factories import (
        HeatFlowFactory,
        HeatFlowIntervalFactory,
        HeatFlowSiteFactory,
        ParentHeatFlowFactory,
    )

    dataset = DatasetFactory(visibility=Visibility.PUBLIC, published=True)
    site = HeatFlowSiteFactory(dataset=dataset)
    interval = HeatFlowIntervalFactory(dataset=dataset, site=site, top=0, bottom=500)
    parent = ParentHeatFlowFactory(
        dataset=dataset, sample=site, value=60, uncertainty=6, comment="as uploaded"
    )
    children = [
        HeatFlowFactory(
            dataset=dataset,
            sample=interval,
            parent=parent,
            is_relevant=index == 0,
            value=100,
            uncertainty=uncertainty,
        )
        for index, uncertainty in enumerate([3, 10, 20])
    ]
    for record in (parent, *children):
        record.refresh_from_db()
    return {
        "dataset": dataset,
        "site": site,
        "interval": interval,
        "parent": parent,
        "children": children,
    }


def parent_data(parent, *chosen, **changes):
    """Post the data a researcher's browser sends for a parent, choosing these children."""
    data = {
        "value": "60",
        "uncertainty": "6",
        "value_unit": "mW / m^2",
        "comment": parent.comment or "",
        "corr_HP_flag": "unknown",
        "relevant_children": [str(child.pk) for child in chosen],
    }
    return {**data, **changes}


def relevant_among(children):
    """Return the pks of the children that are stored as relevant."""
    from heat_flow.models import HeatFlow

    return set(
        HeatFlow.objects.filter(
            pk__in=[child.pk for child in children], is_relevant=True
        ).values_list("pk", flat=True)
    )


class TestParentHeatFlowForm:
    def build(self, records, editor, *chosen, **changes):
        from heat_flow.forms import ParentHeatFlowForm

        return ParentHeatFlowForm(
            instance=records["parent"],
            data=parent_data(records["parent"], *chosen, **changes),
            request=editor(records["dataset"]),
        )

    def elsewhere(self, records, **child_fields):
        """Return a child on another site, and the dataset it was measured in."""
        from tests.factories import (
            HeatFlowFactory,
            HeatFlowIntervalFactory,
            HeatFlowSiteFactory,
        )

        site = HeatFlowSiteFactory(dataset=records["dataset"])
        interval = HeatFlowIntervalFactory(dataset=records["dataset"], site=site)
        return HeatFlowFactory(
            dataset=records["dataset"], sample=interval, **child_fields
        )

    def locked_child(self, records, **child_fields):
        """Return a child at the parent's site, in a dataset nobody here may change."""
        from fairdm.factories import DatasetFactory
        from fairdm.utils.choices import Visibility

        from tests.factories import HeatFlowFactory

        locked = DatasetFactory(visibility=Visibility.PUBLIC, published=True)
        return HeatFlowFactory(
            dataset=locked,
            sample=records["interval"],
            parent=records["parent"],
            value=100,
            uncertainty=10,
            **child_fields,
        )

    def test_it_offers_every_mapped_parent_column_and_the_children_choice(self):
        from heat_flow.forms import ParentHeatFlowForm

        from tests.test_docs.test_field_map import read_mappings

        mapped = {
            mapping.accessor
            for mapping in read_mappings()
            if mapping.accessed_from == "ParentHeatFlow"
        } - {"ghfdb_id", "quality"}

        assert mapped | {"relevant_children"} <= set(ParentHeatFlowForm().fields)

    def test_it_offers_nothing_the_portal_calculates_or_assigns(self):
        from heat_flow.forms import ParentHeatFlowForm

        withheld = {
            "U_score",
            "M_score",
            "quality",
            "quality_scheme",
            "ghfdb_id",
            "dataset",
            "sample",
        }

        assert not withheld & set(ParentHeatFlowForm().fields)

    def test_the_initial_children_are_the_relevant_ones(self, parent_records, editor):
        from heat_flow.forms import ParentHeatFlowForm

        form = ParentHeatFlowForm(
            instance=parent_records["parent"],
            request=editor(parent_records["dataset"]),
        )

        assert set(form.fields["relevant_children"].initial) == {
            parent_records["children"][0].pk
        }

    def test_marking_two_of_three_makes_exactly_those_relevant(
        self, parent_records, editor
    ):
        _first, second, third = parent_records["children"]
        form = self.build(parent_records, editor, second, third)

        assert form.is_valid(), form.errors
        form.save()

        assert relevant_among(parent_records["children"]) == {second.pk, third.pk}

    def test_a_child_at_another_site_is_refused_and_nothing_is_written(
        self, parent_records, editor
    ):
        first, second, _third = parent_records["children"]
        foreign = self.elsewhere(parent_records, is_relevant=False)
        form = self.build(parent_records, editor, second, foreign, comment="changed")

        assert not form.is_valid()
        assert form.has_error("relevant_children", code="other_site")
        parent_records["parent"].refresh_from_db()
        assert parent_records["parent"].comment == "as uploaded"
        assert relevant_among(parent_records["children"]) == {first.pk}
        assert relevant_among([foreign]) == set()

    def test_a_child_at_the_site_that_is_not_the_parents_is_refused_and_nothing_is_written(
        self, parent_records, editor
    ):
        from tests.factories import HeatFlowFactory

        first, second, _third = parent_records["children"]
        unlinked = HeatFlowFactory(
            dataset=parent_records["dataset"],
            sample=parent_records["interval"],
            parent=None,
            is_relevant=False,
            value=100,
            uncertainty=10,
        )
        form = self.build(parent_records, editor, second, unlinked, comment="changed")

        assert not form.is_valid()
        assert form.has_error("relevant_children", code="other_site")
        assert relevant_among([*parent_records["children"], unlinked]) == {first.pk}

    def test_a_child_in_a_dataset_the_researcher_may_not_change_is_refused_when_chosen(
        self, parent_records, editor
    ):
        locked = self.locked_child(parent_records, is_relevant=False)
        form = self.build(parent_records, editor, parent_records["children"][1], locked)

        assert not form.is_valid()
        assert form.has_error("relevant_children")
        assert not form.has_error("relevant_children", code="other_site")
        assert relevant_among([locked]) == set()

    def test_a_child_in_a_dataset_the_researcher_may_not_change_keeps_its_relevance(
        self, parent_records, editor
    ):
        from heat_flow.forms import ParentHeatFlowForm

        locked = self.locked_child(parent_records, is_relevant=True)
        _first, second, _third = parent_records["children"]
        initial = (
            ParentHeatFlowForm(
                instance=parent_records["parent"],
                request=editor(parent_records["dataset"]),
            )
            .fields["relevant_children"]
            .initial
        )
        form = self.build(parent_records, editor, second)

        assert locked.pk not in initial
        assert form.is_valid(), form.errors
        form.save()

        assert relevant_among(parent_records["children"]) == {second.pk}
        assert relevant_among([locked]) == {locked.pk}

    def test_changing_only_the_children_leaves_the_parents_value_unchanged(
        self, parent_records, editor
    ):
        _first, second, third = parent_records["children"]
        form = self.build(parent_records, editor, second, third)

        assert form.is_valid(), form.errors
        form.save()

        parent = parent_records["parent"]
        parent.refresh_from_db()
        assert parent.value.m_as("mW / m^2") == pytest.approx(60)
        assert parent.uncertainty.m_as("mW / m^2") == pytest.approx(6)

    def test_saving_without_commit_then_saving_m2m_marks_the_children(
        self, parent_records, editor
    ):
        first, second, _third = parent_records["children"]
        form = self.build(parent_records, editor, second)

        assert form.is_valid(), form.errors
        form.save(commit=False)
        assert relevant_among(parent_records["children"]) == {first.pk}
        form.save_m2m()

        assert relevant_among(parent_records["children"]) == {second.pk}


class TestFormsForARecordNotYetSaved:
    def test_the_parent_form_builds_and_validates_with_no_instance(self, db):
        from heat_flow.forms import ParentHeatFlowForm

        unbound = ParentHeatFlowForm()
        form = ParentHeatFlowForm(data={"value": "60", "value_unit": "mW / m^2"})

        assert not unbound.children().exists()
        assert not form.children().exists()
        form.full_clean()
        assert form.cleaned_data["relevant_children"].count() == 0

    def test_the_child_form_builds_and_validates_with_no_instance(self, db):
        from types import SimpleNamespace

        from heat_flow.forms import HeatFlowForm

        unbound = HeatFlowForm()
        form = HeatFlowForm(data={"value": "70", "value_unit": "mW / m^2"})
        measurement = SimpleNamespace(sample_id=1)

        form.full_clean()
        assert form.on_own_interval(measurement) is measurement
        assert unbound.on_own_interval(None) is None


class TestParentHeatFlowEditPage:
    def test_a_dataset_owner_marks_two_children_relevant_and_the_quality_moves(
        self, parent_records, researcher
    ):
        from fairdm.contrib.plugins import reverse

        parent = parent_records["parent"]
        _first, second, third = parent_records["children"]
        assert parent.quality == "U1.Mx.-------"
        client = researcher(parent_records["dataset"])

        response = client.post(
            reverse(parent, "edit"), parent_data(parent, second, third)
        )

        assert response.status_code == 302
        parent.refresh_from_db()
        assert relevant_among(parent_records["children"]) == {second.pk, third.pk}
        assert parent.quality == "U3.Mx.-------"
