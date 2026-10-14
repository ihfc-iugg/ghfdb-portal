# Tests for the depth interval, the child heat flow and its sub-measurements. Mirrors
# ``project/heat_flow/models/child.py``.

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError


class TestHeatFlowInterval:
    def test_site_fk_is_named_site_and_targets_heat_flow_site(self):
        # The interval-to-site link is called ``site`` and is typed against
        # ``HeatFlowSite``, not the polymorphic ``Sample`` root.
        from heat_flow.models import HeatFlowInterval, HeatFlowSite

        field = HeatFlowInterval._meta.get_field("site")
        assert field.related_model is HeatFlowSite
        assert field.remote_field.related_name == "intervals"
        assert "parent" not in str(field.verbose_name).lower()

    @pytest.mark.django_db
    def test_interval_links_to_site(self, dataset, site_fixture):
        # HeatFlowInterval.site FK resolves to site; reverse 'intervals' accessor
        # works (FS-001 US-1 scenario 2, A9).
        from heat_flow.models import HeatFlowInterval

        interval = HeatFlowInterval.objects.create(
            dataset=dataset,
            site=site_fixture,
            name="Depth Interval",
            top=0,
            bottom=500,
        )
        loaded = HeatFlowInterval.objects.get(pk=interval.pk)
        assert loaded.site == site_fixture
        assert site_fixture.intervals.filter(pk=interval.pk).exists()

    @pytest.mark.django_db
    def test_sub_measurements_on_interval(
        self, dataset, interval_fixture, gradient_fixture, conductivity_fixture
    ):
        # ThermalGradient and IntervalConductivity link to interval and appear in
        # interval.measurements; Pint Quantity attributes present on value and depth
        # fields (FS-001 FR-006, A5, US-1 scenario 3).
        measurements = list(interval_fixture.measurements.all())
        pks = [m.pk for m in measurements]
        assert gradient_fixture.pk in pks
        assert conductivity_fixture.pk in pks

        # Reload from DB to exercise the Pint field descriptors
        from heat_flow.models import HeatFlowInterval, ThermalGradient

        g = ThermalGradient.objects.get(pk=gradient_fixture.pk)
        assert hasattr(g.value, "magnitude")
        assert float(g.value.magnitude) == pytest.approx(25.0)

        interval = HeatFlowInterval.objects.get(pk=interval_fixture.pk)
        assert hasattr(interval.top, "magnitude")
        assert hasattr(interval.bottom, "magnitude")

    @pytest.mark.django_db
    def test_zero_thickness_interval_rejected(self, dataset, site_fixture):
        # HeatFlowInterval.full_clean() raises ValidationError when top >= bottom
        # (EC-001, M4).
        from heat_flow.models import HeatFlowInterval

        interval = HeatFlowInterval(
            dataset=dataset,
            site=site_fixture,
            name="Zero Thickness",
            top=100,
            bottom=100,
        )
        with pytest.raises(ValidationError):
            interval.full_clean()

    @pytest.mark.django_db
    def test_valid_interval_passes_clean(self, dataset, site_fixture):
        from heat_flow.models import HeatFlowInterval

        interval = HeatFlowInterval(
            dataset=dataset,
            site=site_fixture,
            name="Valid Interval",
            top=0,
            bottom=500,
        )
        interval.full_clean()  # must not raise

    @pytest.mark.django_db
    def test_deleting_a_site_deletes_its_intervals(
        self, dataset, site_fixture, interval_fixture
    ):
        # Deleting a HeatFlowSite deletes its HeatFlowInterval records (FS-001 FR-007,
        # site FK is on_delete=CASCADE).
        from heat_flow.models import HeatFlowInterval

        interval_pk = interval_fixture.pk

        site_fixture.delete()

        assert not HeatFlowInterval.objects.filter(pk=interval_pk).exists()


class TestHeatFlow:
    @pytest.mark.django_db
    def test_heat_flow_child_relationships(
        self,
        dataset,
        site_fixture,
        interval_fixture,
        gradient_fixture,
        conductivity_fixture,
        parent_fixture,
        child_fixture,
    ):
        # Forward and reverse FK relationships on HeatFlow child resolve
        # correctly; default US/MS score values are Ux/Mx on a fresh instance
        # (FS-001 FR-014, A11, US-1 scenario 4).
        from heat_flow.models import HeatFlow
        from heat_flow.utils import MScoreOptions, UScoreOptions

        child = HeatFlow.objects.get(pk=child_fixture.pk)
        assert child.sample == interval_fixture
        assert child.parent == parent_fixture
        assert child.thermal_gradient == gradient_fixture
        assert child.thermal_conductivity == conductivity_fixture
        assert parent_fixture.children.filter(pk=child.pk).exists()

        # Default quality scores on a freshly created instance without uncertainty data
        fresh = HeatFlow.objects.create(
            dataset=dataset,
            sample=interval_fixture,
            name="Fresh Child",
            value=50.0,
        )
        assert fresh.U_score == UScoreOptions.Ux
        assert fresh.M_score == MScoreOptions.Mx

    @pytest.mark.django_db
    def test_surface_temperature_persists_for_marine_and_continental_readings(
        self, dataset, interval_fixture
    ):
        # The 2026.03 template renames ``water_temperature`` to ``Surface_temperature``
        # (C24) because the value applies to both marine and continental measurements,
        # not just marine ones.
        from heat_flow.models import HeatFlow

        child = HeatFlow.objects.create(
            dataset=dataset,
            sample=interval_fixture,
            name="Continental reading",
            value=50.0,
            surface_temperature=12.5,
        )
        reloaded = HeatFlow.objects.get(pk=child.pk)
        assert hasattr(reloaded.surface_temperature, "magnitude")
        assert float(reloaded.surface_temperature.magnitude) == pytest.approx(12.5)
        assert not hasattr(reloaded, "water_temperature")

    @pytest.mark.django_db
    def test_heat_flow_save_rejects_wrong_sample(self, site_fixture, child_fixture):
        # HeatFlow.save() raises ValidationError when sample is a HeatFlowSite
        # (wrong type); only HeatFlowInterval is valid (FS-001 FR-010a).
        with pytest.raises(ValidationError):
            child_fixture.sample = site_fixture
            child_fixture.save()

    @pytest.mark.django_db
    def test_multiple_heatflow_can_share_gradient(
        self, dataset, interval_fixture, gradient_fixture, parent_fixture
    ):
        # Two HeatFlow children may reference the same ThermalGradient FK without
        # IntegrityError (FS-001 FR-013).
        from heat_flow.models import HeatFlow

        hf1 = HeatFlow.objects.create(
            dataset=dataset,
            sample=interval_fixture,
            name="Child A",
            value=60.0,
            thermal_gradient=gradient_fixture,
        )
        hf2 = HeatFlow.objects.create(
            dataset=dataset,
            sample=interval_fixture,
            name="Child B",
            value=65.0,
            thermal_gradient=gradient_fixture,
        )
        assert hf1.pk is not None
        assert hf2.pk is not None
        assert gradient_fixture.heat_flow_children.count() == 2

    @pytest.mark.django_db
    def test_multiple_heatflow_can_share_conductivity(
        self, dataset, interval_fixture, conductivity_fixture, parent_fixture
    ):
        # Two HeatFlow children may reference the same IntervalConductivity FK
        # without IntegrityError (FS-001 FR-017), the conductivity half alongside the
        # gradient case above.
        from heat_flow.models import HeatFlow

        hf1 = HeatFlow.objects.create(
            dataset=dataset,
            sample=interval_fixture,
            name="Child A",
            value=60.0,
            thermal_conductivity=conductivity_fixture,
        )
        hf2 = HeatFlow.objects.create(
            dataset=dataset,
            sample=interval_fixture,
            name="Child B",
            value=65.0,
            thermal_conductivity=conductivity_fixture,
        )
        assert hf1.pk is not None
        assert hf2.pk is not None
        assert conductivity_fixture.heat_flow_children.count() == 2

    @pytest.mark.django_db
    def test_gradient_referenced_by_a_child_cannot_be_deleted(
        self, dataset, interval_fixture, gradient_fixture
    ):
        # A ThermalGradient referenced by a HeatFlow child is protected from
        # deletion (FS-001 FR-017, on_delete=PROTECT).
        from django.db.models import ProtectedError
        from heat_flow.models import HeatFlow

        HeatFlow.objects.create(
            dataset=dataset,
            sample=interval_fixture,
            name="Protects gradient",
            value=60.0,
            thermal_gradient=gradient_fixture,
        )

        with pytest.raises(ProtectedError):
            gradient_fixture.delete()

    @pytest.mark.django_db
    def test_conductivity_referenced_by_a_child_cannot_be_deleted(
        self, dataset, interval_fixture, conductivity_fixture
    ):
        # An IntervalConductivity referenced by a HeatFlow child is protected
        # from deletion (FS-001 FR-017, on_delete=PROTECT).
        from django.db.models import ProtectedError
        from heat_flow.models import HeatFlow

        HeatFlow.objects.create(
            dataset=dataset,
            sample=interval_fixture,
            name="Protects conductivity",
            value=60.0,
            thermal_conductivity=conductivity_fixture,
        )

        with pytest.raises(ProtectedError):
            conductivity_fixture.delete()

    @pytest.mark.django_db
    def test_heat_flow_allows_null_gradient_and_conductivity(
        self, dataset, interval_fixture
    ):
        # A HeatFlow with neither gradient nor conductivity is valid; incomplete
        # records must not be blocked at entry time (EC-002, M2).
        from heat_flow.models import HeatFlow

        child = HeatFlow.objects.create(
            dataset=dataset,
            sample=interval_fixture,
            name="Incomplete Child",
            value=50.0,
            thermal_gradient=None,
            thermal_conductivity=None,
        )
        assert child.pk is not None

    @pytest.mark.django_db
    def test_heat_flow_is_probe_property(
        self, dataset, site_fixture, interval_fixture, child_fixture
    ):
        # HeatFlow.is_probe is True when the linked interval has probe metadata;
        # False otherwise (FS-001 US-3 independent test).
        from heat_flow.models import HeatFlow, HeatFlowInterval, ProbeMetadata

        # Attach probe metadata to the existing interval
        ProbeMetadata.objects.create(interval=interval_fixture, penetration=3.5)
        # Reload to clear cached_property
        child = HeatFlow.objects.get(pk=child_fixture.pk)
        assert child.is_probe is True

        # A child whose interval has NO probe metadata
        other_interval = HeatFlowInterval.objects.create(
            dataset=dataset,
            site=site_fixture,
            name="No Probe",
            top=600,
            bottom=900,
        )
        other_child = HeatFlow.objects.create(
            dataset=dataset,
            sample=other_interval,
            name="No Probe Child",
            value=50.0,
        )
        assert other_child.is_probe is False


class TestHeatFlowCorrection:
    @pytest.mark.django_db
    def test_heat_flow_corrections(self, dataset, interval_fixture, child_fixture):
        # HeatFlowCorrection records link via FK and are accessible via
        # child.corrections (FS-001 US-1 scenario 5).
        from heat_flow.models import HeatFlowCorrection

        HeatFlowCorrection.objects.create(
            heat_flow=child_fixture,
            correction_type="IS",
            status="present_corrected",
        )
        HeatFlowCorrection.objects.create(
            heat_flow=child_fixture,
            correction_type="T",
            status="not_considered",
        )
        assert child_fixture.corrections.count() == 2

    @pytest.mark.django_db
    def test_correction_valid_status_accepted(self, child_fixture):
        from heat_flow.models import HeatFlowCorrection

        corr = HeatFlowCorrection(
            heat_flow=child_fixture, correction_type="IS", status="tilt_corrected"
        )
        corr.save()  # must not raise
        assert corr.pk is not None

    @pytest.mark.django_db
    def test_correction_invalid_status_rejected(self, child_fixture):
        # Invalid status/type combinations raise ValidationError from save()
        # (FS-001 FR-021): - IS + considered_p (considered_p only valid for environmental
        # types) - S + tilt_corrected (tilt_corrected only valid for IS) - T +.
        from heat_flow.models import HeatFlowCorrection

        with pytest.raises(ValidationError):
            HeatFlowCorrection(
                heat_flow=child_fixture, correction_type="IS", status="considered_p"
            ).save()

        with pytest.raises(ValidationError):
            HeatFlowCorrection(
                heat_flow=child_fixture, correction_type="S", status="tilt_corrected"
            ).save()

        with pytest.raises(ValidationError):
            HeatFlowCorrection(
                heat_flow=child_fixture,
                correction_type="T",
                status="present_not_significant",
            ).save()

    @pytest.mark.django_db
    def test_correction_unspecified_always_valid(self, child_fixture):
        from heat_flow.models import HeatFlowCorrection

        for ct in ["IS", "T", "S", "E", "TOPO", "PAL", "SUR", "CONV", "HR"]:
            corr = HeatFlowCorrection(
                heat_flow=child_fixture, correction_type=ct, status="-"
            )
            corr.save()  # must not raise

    @pytest.mark.django_db
    def test_second_correction_of_the_same_type_rejected(self, child_fixture):
        # A second HeatFlowCorrection of the same correction_type on one child is
        # rejected: Meta.unique_together = ("heat_flow", "correction_type")
        # (FS-001 FR-027).
        from heat_flow.models import HeatFlowCorrection

        HeatFlowCorrection.objects.create(
            heat_flow=child_fixture, correction_type="IS", status="present_corrected"
        )
        with pytest.raises(IntegrityError):
            HeatFlowCorrection.objects.create(
                heat_flow=child_fixture,
                correction_type="IS",
                status="not_considered",
            )

    @pytest.mark.django_db
    def test_correction_invalid_type_rejected(self, child_fixture):
        # A correction with an unrecognised correction_type is rejected by
        # Django's field-level choices validation when full_clean() is called (EC-004,
        # L1).
        from heat_flow.models import HeatFlowCorrection

        corr = HeatFlowCorrection(
            heat_flow=child_fixture, correction_type="INVALID_TYPE", status="-"
        )
        with pytest.raises(ValidationError):
            corr.full_clean()


class TestThermalGradient:
    @pytest.mark.django_db
    def test_thermal_gradient_save_rejects_wrong_sample(
        self, site_fixture, gradient_fixture
    ):
        # ThermalGradient.save() raises ValidationError when sample is a
        # HeatFlowSite (FS-001 FR-016a).
        with pytest.raises(ValidationError):
            gradient_fixture.sample = site_fixture
            gradient_fixture.save()

    @pytest.mark.django_db
    def test_value_non_nullable_thermal_gradient(self, dataset, interval_fixture):
        # ThermalGradient.value is non-nullable; omitting it raises an
        # IntegrityError at the database layer.
        from heat_flow.models import ThermalGradient

        with pytest.raises((IntegrityError, ValidationError)):
            ThermalGradient.objects.create(
                dataset=dataset, sample=interval_fixture, name="No Value"
            )

    @pytest.mark.django_db
    def test_gradient_corrected_value_methods_shutin_and_count_persist(
        self, dataset, interval_fixture
    ):
        # A gradient's corrected value, its top and bottom temperature methods,
        # its shut-in times and its recording count persist and read back
        # (FS-001 FR-019).
        from heat_flow import vocabularies
        from heat_flow.models import ThermalGradient
        from research_vocabs.models import Concept

        gradient = ThermalGradient.objects.create(
            dataset=dataset,
            sample=interval_fixture,
            name="Gradient with corrections",
            value=25.0,
            corrected_value=27.5,
            corrected_uncertainty=1.2,
            shutin_top=10,
            shutin_bottom=15,
            number=8,
        )
        top_method = Concept.get_for_vocabulary(vocabularies.TemperatureMethod).first()
        bottom_method = (
            Concept.get_for_vocabulary(vocabularies.TemperatureMethod).exclude(
                pk=top_method.pk
            )
            or Concept.get_for_vocabulary(vocabularies.TemperatureMethod)
        ).first()
        gradient.method_top.add(top_method)
        gradient.method_bottom.add(bottom_method)

        reloaded = ThermalGradient.objects.get(pk=gradient.pk)

        assert hasattr(reloaded.corrected_value, "magnitude")
        assert float(reloaded.corrected_value.magnitude) == pytest.approx(27.5)
        assert hasattr(reloaded.corrected_uncertainty, "magnitude")
        assert float(reloaded.corrected_uncertainty.magnitude) == pytest.approx(1.2)

        assert list(reloaded.method_top.values_list("pk", flat=True)) == [top_method.pk]
        assert list(reloaded.method_bottom.values_list("pk", flat=True)) == [
            bottom_method.pk
        ]

        assert hasattr(reloaded.shutin_top, "magnitude")
        assert float(reloaded.shutin_top.magnitude) == pytest.approx(10)
        assert hasattr(reloaded.shutin_bottom, "magnitude")
        assert float(reloaded.shutin_bottom.magnitude) == pytest.approx(15)

        assert reloaded.number == 8

    @pytest.mark.django_db
    def test_top_and_bottom_absolute_temperatures_persist(
        self, dataset, interval_fixture
    ):
        # The 2026.03 template adds four columns (C50-C53) carrying the absolute
        # temperatures used to calculate the gradient: the mean and uncertainty at the
        # top and bottom of the heat-flow determination interval.
        from heat_flow.models import ThermalGradient

        gradient = ThermalGradient.objects.create(
            dataset=dataset,
            sample=interval_fixture,
            name="Gradient with absolute temperatures",
            value=25.0,
            temperature_top=8.2,
            temperature_top_uncertainty=0.5,
            temperature_bottom=45.7,
            temperature_bottom_uncertainty=0.8,
        )

        reloaded = ThermalGradient.objects.get(pk=gradient.pk)

        assert hasattr(reloaded.temperature_top, "magnitude")
        assert float(reloaded.temperature_top.magnitude) == pytest.approx(8.2)
        assert hasattr(reloaded.temperature_top_uncertainty, "magnitude")
        assert float(reloaded.temperature_top_uncertainty.magnitude) == pytest.approx(
            0.5
        )
        assert hasattr(reloaded.temperature_bottom, "magnitude")
        assert float(reloaded.temperature_bottom.magnitude) == pytest.approx(45.7)
        assert hasattr(reloaded.temperature_bottom_uncertainty, "magnitude")
        assert float(
            reloaded.temperature_bottom_uncertainty.magnitude
        ) == pytest.approx(0.8)


class TestIntervalConductivity:
    @pytest.mark.django_db
    def test_interval_conductivity_save_rejects_wrong_sample(
        self, site_fixture, conductivity_fixture
    ):
        # IntervalConductivity.save() raises ValidationError when sample is a
        # HeatFlowSite (FS-001 FR-018a).
        with pytest.raises(ValidationError):
            conductivity_fixture.sample = site_fixture
            conductivity_fixture.save()

    @pytest.mark.django_db
    def test_value_non_nullable_interval_conductivity(self, dataset, interval_fixture):
        # IntervalConductivity.value is non-nullable; omitting it raises an
        # IntegrityError at the database layer.
        from heat_flow.models import IntervalConductivity

        with pytest.raises((IntegrityError, ValidationError)):
            IntervalConductivity.objects.create(
                dataset=dataset, sample=interval_fixture, name="No Value"
            )

    @pytest.mark.django_db
    def test_conductivity_vocabulary_fields_count_and_score_persist(
        self, dataset, interval_fixture
    ):
        # A conductivity's vocabulary fields, its determination count and its
        # score persist and read back (FS-001 FR-021).
        from heat_flow import vocabularies
        from heat_flow.models import IntervalConductivity
        from research_vocabs.models import Concept

        conductivity = IntervalConductivity.objects.create(
            dataset=dataset,
            sample=interval_fixture,
            name="Conductivity with vocab fields",
            value=2.5,
            number=12,
            score=0.9,
        )

        vocab_fields = {
            "source": vocabularies.ConductivitySource,
            "location": vocabularies.ConductivityLocation,
            "method": vocabularies.ConductivityMethod,
            "saturation": vocabularies.ConductivitySaturation,
            "pT_conditions": vocabularies.ConductivityPTConditions,
            "pT_function": vocabularies.ConductivityPTFunction,
            "strategy": vocabularies.ConductivityStrategy,
        }
        expected_pks = {}
        for field_name, vocabulary in vocab_fields.items():
            concept = Concept.get_for_vocabulary(vocabulary).first()
            getattr(conductivity, field_name).add(concept)
            expected_pks[field_name] = concept.pk

        reloaded = IntervalConductivity.objects.get(pk=conductivity.pk)

        for field_name, expected_pk in expected_pks.items():
            assert list(getattr(reloaded, field_name).values_list("pk", flat=True)) == [
                expected_pk
            ]

        assert reloaded.number == 12
        # The score is calculated (FR-002), not kept as supplied. This interval's site
        # records no exploration method, so the score is not determined.
        assert reloaded.score is None


class TestProbeMetadata:
    @pytest.mark.django_db
    def test_probe_metadata_linked_to_interval(
        self, dataset, site_fixture, interval_fixture
    ):
        # ProbeMetadata can be created for an interval; all fields readable via
        # interval.probe_metadata (FS-001 US-3 scenario 1).
        from heat_flow.models import ProbeMetadata

        ProbeMetadata.objects.create(
            interval=interval_fixture,
            penetration=3.5,
            length=5.0,
            tilt=2.0,
        )
        reloaded = type(interval_fixture).objects.get(pk=interval_fixture.pk)
        assert float(reloaded.probe_metadata.penetration.magnitude) == pytest.approx(
            3.5
        )
        assert float(reloaded.probe_metadata.length.magnitude) == pytest.approx(5.0)
        assert float(reloaded.probe_metadata.tilt.magnitude) == pytest.approx(2.0)

    @pytest.mark.django_db
    def test_probe_metadata_accepts_several_probe_type_concepts(
        self, dataset, interval_fixture
    ):
        # ProbeMetadata.probe_type accepts several probe type concepts and reads
        # them back (FS-001 FR-023, many-to-many vocabulary field).
        from heat_flow import vocabularies
        from heat_flow.models import ProbeMetadata
        from research_vocabs.models import Concept

        probe = ProbeMetadata.objects.create(interval=interval_fixture, penetration=3.5)
        concepts = list(Concept.get_for_vocabulary(vocabularies.ProbeType)[:2])
        assert len(concepts) == 2, "fixture requires at least two probe type concepts"
        probe.probe_type.set(concepts)

        reloaded = ProbeMetadata.objects.get(pk=probe.pk)
        assert set(reloaded.probe_type.values_list("pk", flat=True)) == {
            c.pk for c in concepts
        }

    @pytest.mark.django_db
    def test_interval_without_probe_raises(self, dataset, site_fixture):
        # Accessing probe_metadata on an interval with none raises
        # RelatedObjectDoesNotExist (FS-001 US-3 scenario 2).
        from heat_flow.models import HeatFlowInterval, ProbeMetadata

        fresh_interval = HeatFlowInterval.objects.create(
            dataset=dataset,
            site=site_fixture,
            name="No Probe Interval",
            top=600,
            bottom=900,
        )
        with pytest.raises(ProbeMetadata.DoesNotExist):
            _ = fresh_interval.probe_metadata

    @pytest.mark.django_db
    def test_probe_metadata_cascade_on_interval_delete(
        self, dataset, site_fixture, interval_fixture
    ):
        # Deleting the interval also deletes its ProbeMetadata (CASCADE; FS-001 US-3
        # scenario 3, SC-004).
        from heat_flow.models import ProbeMetadata

        probe = ProbeMetadata.objects.create(interval=interval_fixture, penetration=3.5)
        probe_pk = probe.pk
        interval_fixture.delete()
        assert not ProbeMetadata.objects.filter(pk=probe_pk).exists()


class TestCorrectionStatusDocumentation:
    # The documented status table must match the one the code enforces. FS-001 FR-028
    # requires the valid combinations to be documented.

    DOC = "docs/ghfdb_fields.md"
    HEADING = "##### Valid status per disturbance type"

    def _documented_statuses(self):
        """Map each disturbance type in the documented table to its statuses."""
        import re
        from pathlib import Path

        text = Path(__file__).resolve().parents[3].joinpath(self.DOC).read_text()
        section = text.split(self.HEADING, 1)[1]
        documented = {}
        for line in section.splitlines():
            if not line.startswith("|") or line.startswith("| ---"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) != 2 or cells[0] == "Disturbance type":
                continue
            types = re.findall(r"\b([A-Z]{1,4})\b(?=\s*\()", cells[0])
            statuses = {
                s.strip().replace("\\", "").replace("unspecified (`-`)", "-")
                for s in cells[1].split(",")
            }
            for code in types:
                documented[code] = statuses
        return documented

    def test_documented_statuses_match_the_enforced_ones(self):
        from heat_flow.models import HeatFlowCorrection

        documented = self._documented_statuses()
        assert documented, "No documented status table found under the heading."

        for code, _label in HeatFlowCorrection.CorrectionTypeChoices.choices:
            enforced = HeatFlowCorrection.VALID_STATUS_FOR_TYPE.get(code)
            if enforced is None:
                enforced = HeatFlowCorrection.ENVIRONMENTAL_VALID
            assert code in documented, f"{code} is enforced and not documented."
            assert documented[code] == set(enforced), (
                f"Documented statuses for {code} do not match the code.\n"
                f"  documented: {sorted(documented[code])}\n"
                f"  enforced:   {sorted(enforced)}"
            )


class TestMeasurementScores:
    """A gradient and a conductivity store their own uncorrected score (FS-007 US1)."""

    @staticmethod
    def concepts(vocabulary, *names):
        from research_vocabs.models import Concept

        return list(Concept.get_for_vocabulary(vocabulary).filter(name__in=names))

    def probe_interval(self):
        from tests.factories import (
            HeatFlowIntervalFactory,
            HeatFlowSiteFactory,
            ProbeMetadataFactory,
        )

        site = HeatFlowSiteFactory(explo_method="probing_offshore", elevation=-3000)
        interval = HeatFlowIntervalFactory(site=site)
        ProbeMetadataFactory(
            interval=interval, penetration=12, tilt=45, probe_type=[]
        )
        return interval

    def borehole_interval(self, **depths):
        from tests.factories import HeatFlowIntervalFactory, HeatFlowSiteFactory

        site = HeatFlowSiteFactory(explo_method="drilling")
        return HeatFlowIntervalFactory(site=site, **depths)

    def reload(self, measurement):
        return type(measurement).objects.get(pk=measurement.pk)

    @pytest.mark.django_db
    def test_a_saved_probe_gradient_stores_its_score_and_the_revision(self):
        from tests.factories import ThermalGradientFactory

        gradient = ThermalGradientFactory(
            sample=self.probe_interval(), number=6, method_top=[], method_bottom=[]
        )

        stored = self.reload(gradient)
        # 1.0, +0.1 penetration, +0.1 recordings, 0 water depth, -0.2 tilt: nothing is
        # waived because the score reads no child.
        assert stored.score == pytest.approx(1.0)
        assert stored.score_missing is False
        assert stored.quality_scheme == "hfqa_tool 0.2"

    @pytest.mark.django_db
    def test_a_saved_borehole_gradient_is_scored_by_the_borehole_rules(self):
        from heat_flow import vocabularies
        from tests.factories import ThermalGradientFactory

        logs = self.concepts(vocabularies.TemperatureMethod, "LOGeq")
        gradient = ThermalGradientFactory(
            sample=self.borehole_interval(),
            number=10,
            method_top=logs,
            method_bottom=logs,
        )

        stored = self.reload(gradient)
        assert stored.score == pytest.approx(1.1)
        assert stored.score_missing is False

    @pytest.mark.django_db
    def test_a_gradient_at_a_site_without_an_exploration_method_is_not_determined(
        self,
    ):
        from tests.factories import (
            HeatFlowIntervalFactory,
            HeatFlowSiteFactory,
            ThermalGradientFactory,
        )

        interval = HeatFlowIntervalFactory(
            site=HeatFlowSiteFactory(explo_method=None)
        )
        gradient = ThermalGradientFactory(
            sample=interval, score=0.7, method_top=[], method_bottom=[]
        )

        stored = self.reload(gradient)
        assert stored.score is None
        assert stored.score_missing is False
        assert stored.quality_scheme == "hfqa_tool 0.2"

    @pytest.mark.django_db
    def test_adding_removing_and_clearing_a_method_recalculates_the_score(self):
        from heat_flow import vocabularies
        from tests.factories import ThermalGradientFactory

        logs = self.concepts(vocabularies.TemperatureMethod, "LOGeq")
        gradient = ThermalGradientFactory(
            sample=self.borehole_interval(),
            number=10,
            method_top=[],
            method_bottom=[],
        )
        assert self.reload(gradient).score_missing is True

        gradient.method_top.add(*logs)
        gradient.method_bottom.add(*logs)
        assert self.reload(gradient).score == pytest.approx(1.1)
        assert self.reload(gradient).score_missing is False

        gradient.method_bottom.remove(*logs)
        assert self.reload(gradient).score == pytest.approx(1.1)

        gradient.method_top.clear()
        emptied = self.reload(gradient)
        assert emptied.score == pytest.approx(0.5)
        assert emptied.score_missing is True

    @pytest.mark.django_db
    def test_one_gradient_used_by_two_children_keeps_one_score(self):
        from heat_flow.models import HeatFlowCorrection
        from tests.factories import (
            HeatFlowCorrectionFactory,
            HeatFlowFactory,
            ThermalGradientFactory,
        )

        interval = self.probe_interval()
        gradient = ThermalGradientFactory(
            sample=interval, number=6, method_top=[], method_bottom=[]
        )
        corrected = HeatFlowFactory(sample=interval, thermal_gradient=gradient)
        uncorrected = HeatFlowFactory(sample=interval, thermal_gradient=gradient)
        HeatFlowCorrectionFactory(
            heat_flow=corrected,
            correction_type=HeatFlowCorrection.CorrectionTypeChoices.SUR,
            status=HeatFlowCorrection.StatusChoices.PRESENT_CORRECTED,
        )

        scores = {
            type(child).objects.get(pk=child.pk).thermal_gradient.score
            for child in (corrected, uncorrected)
        }

        assert scores == {self.reload(gradient).score}
        assert self.reload(gradient).score == pytest.approx(1.0)

    @pytest.mark.django_db
    def test_a_saved_borehole_conductivity_stores_its_score_and_the_revision(self):
        from heat_flow import vocabularies
        from tests.factories import IntervalConductivityFactory

        conductivity = IntervalConductivityFactory(
            sample=self.borehole_interval(top=0, bottom=500),
            number=30,
            source=self.concepts(vocabularies.ConductivitySource, "core_samples"),
            location=self.concepts(vocabularies.ConductivityLocation, "actual"),
            saturation=self.concepts(
                vocabularies.ConductivitySaturation, "saturatedMeasured"
            ),
            pT_conditions=self.concepts(
                vocabularies.ConductivityPTConditions, "actualInSitu"
            ),
        )

        stored = self.reload(conductivity)
        assert stored.score == pytest.approx(1.0)
        assert stored.score_missing is False
        assert stored.quality_scheme == "hfqa_tool 0.2"

    @pytest.mark.django_db
    def test_a_probe_conductivity_can_score_above_one(self):
        from heat_flow import vocabularies
        from tests.factories import IntervalConductivityFactory

        conductivity = IntervalConductivityFactory(
            sample=self.probe_interval(),
            number=4,
            source=self.concepts(vocabularies.ConductivitySource, "insitu_probe"),
            location=self.concepts(vocabularies.ConductivityLocation, "actual"),
            method=self.concepts(vocabularies.ConductivityMethod, "probePulse"),
            saturation=self.concepts(
                vocabularies.ConductivitySaturation, "saturatedInSitu"
            ),
            pT_conditions=self.concepts(
                vocabularies.ConductivityPTConditions, "actualInSitu"
            ),
        )

        assert self.reload(conductivity).score == pytest.approx(1.2)

    @pytest.mark.django_db
    def test_a_conductivity_without_interval_depths_takes_the_gate_score(self):
        from tests.factories import IntervalConductivityFactory

        conductivity = IntervalConductivityFactory(
            sample=self.borehole_interval(),
            number=30,
            source=[],
            location=[],
            saturation=[],
            pT_conditions=[],
        )

        stored = self.reload(conductivity)
        assert stored.score == pytest.approx(0.1)
        assert stored.score_missing is True

    @pytest.mark.django_db
    def test_changing_a_conductivity_concept_recalculates_the_score(self):
        from heat_flow import vocabularies
        from tests.factories import IntervalConductivityFactory

        conductivity = IntervalConductivityFactory(
            sample=self.borehole_interval(top=0, bottom=500),
            number=30,
            source=self.concepts(vocabularies.ConductivitySource, "core_samples"),
            location=self.concepts(vocabularies.ConductivityLocation, "actual"),
            saturation=self.concepts(
                vocabularies.ConductivitySaturation, "saturatedMeasured"
            ),
            pT_conditions=[],
        )
        assert self.reload(conductivity).score_missing is True

        conductivity.pT_conditions.add(
            *self.concepts(vocabularies.ConductivityPTConditions, "recordedAmbient")
        )
        ambient = self.reload(conductivity)
        assert ambient.score == pytest.approx(0.8)
        assert ambient.score_missing is False

        conductivity.source.clear()
        assert self.reload(conductivity).score_missing is True

    @pytest.mark.parametrize(
        ("model_name", "field_name"),
        [
            (model_name, field_name)
            for model_name in ("ThermalGradient", "IntervalConductivity")
            for field_name in ("score", "score_missing", "quality_scheme")
        ],
    )
    def test_every_new_score_field_has_a_verbose_name_and_help_text(
        self, model_name, field_name
    ):
        from heat_flow import models

        field = getattr(models, model_name)._meta.get_field(field_name)

        assert str(field.verbose_name).strip()
        assert str(field.help_text).strip()


# Corrections the model refuses today (research R5), so these conformance cases reach the
# child only through the scheme (tests/test_heat_flow/test_quality.py). The tilt waiver
# (P1) and the borehole pT agreement (B1, B5, B7, B8) wait for the maintainer's ruling.
UNSTORABLE_CASES = {
    "P1-probe-with-waivers",
    "B1-agreeing-in-situ",
    "B5-drilling-clustering",
    "B7-unresolvable-surface-case",
    "B8-indirect-no-methods",
}


def storable_cases():
    from tests.test_heat_flow.test_quality import CONFORMANCE_CASES

    return [case for case in CONFORMANCE_CASES if case.id not in UNSTORABLE_CASES]


class TestChildScores:
    """A child stores its U-score, corrected T and TC, M-score and code (FS-007 US2)."""

    @staticmethod
    def build_child(inputs, *, value=50, uncertainty=None, corrections=None):
        """Build the child of a conformance case with exactly the corrections given."""
        from tests.factories import HeatFlowCorrectionFactory, HeatFlowFactory
        from tests.test_heat_flow.test_quality import build_case

        site, gradient, conductivity = build_case(inputs)
        child = HeatFlowFactory(
            sample=gradient.sample,
            value=value,
            uncertainty=uncertainty,
            thermal_gradient=gradient,
            thermal_conductivity=conductivity,
        )
        for correction_type, status in (corrections or {}).items():
            HeatFlowCorrectionFactory(
                heat_flow=child, correction_type=correction_type, status=status
            )
        return child

    @staticmethod
    def reload(child):
        from heat_flow.models import HeatFlow

        return HeatFlow.objects.get(pk=child.pk)

    @staticmethod
    def inputs_of(case_id):
        from tests.test_heat_flow.test_quality import CONFORMANCE_CASES

        return next(c.values[0] for c in CONFORMANCE_CASES if c.id == case_id)

    @pytest.mark.django_db
    @pytest.mark.parametrize("inputs", storable_cases())
    def test_the_stored_scores_equal_the_toolbox_output(self, inputs, request):
        from tests.test_heat_flow.test_quality import SCHEME_EXPECTATIONS

        value, uncertainty, statuses, u, m, flags = SCHEME_EXPECTATIONS[
            request.node.callspec.id
        ]
        corrections = dict(statuses)
        if inputs.get("in_situ") is not None:
            corrections["IS"] = inputs["in_situ"]

        stored = self.reload(
            self.build_child(
                inputs,
                value=value or 50,
                uncertainty=uncertainty,
                corrections=corrections,
            )
        )

        assert stored.T_score == pytest.approx(inputs["T"])
        assert stored.TC_score == pytest.approx(inputs["TC"])
        assert stored.U_score == u
        assert stored.M_score == m
        assert stored.quality == f"{u}.{m}.{flags}"
        assert stored.quality_scheme == "hfqa_tool 0.2"

    @pytest.mark.django_db
    @pytest.mark.parametrize("explo_method", ["other", None])
    def test_a_site_with_no_route_leaves_the_sub_scores_not_determined(
        self, explo_method
    ):
        from tests.factories import HeatFlowFactory
        from tests.test_heat_flow.test_quality import build_case

        inputs = dict(self.inputs_of("B2-not-considered"), explo=explo_method)
        _site, gradient, conductivity = build_case(inputs)

        stored = self.reload(
            HeatFlowFactory(
                sample=gradient.sample,
                value=70,
                uncertainty=7,
                thermal_gradient=gradient,
                thermal_conductivity=conductivity,
            )
        )

        assert stored.T_score is None
        assert stored.TC_score is None
        assert stored.U_score == "U2"
        assert stored.M_score == "Mx"
        assert stored.quality == "U2.Mx.-------"

    @pytest.mark.django_db
    def test_a_child_without_a_gradient_or_a_conductivity_is_not_determined(self):
        from tests.factories import HeatFlowFactory, HeatFlowIntervalFactory

        child = HeatFlowFactory(
            sample=HeatFlowIntervalFactory(), value=70, uncertainty=7
        )

        stored = self.reload(child)

        assert stored.T_score is None
        assert stored.TC_score is None
        assert stored.M_score == "Mx"
        assert stored.quality == "U2.Mx.-------"

    @pytest.mark.django_db
    def test_the_marks_of_the_two_sub_scores_are_stored_apart(self):
        stored = self.reload(self.build_child(self.inputs_of("X5-interval-gate")))

        # The interval gate marks the conductivity; the gradient's inputs are all present.
        assert stored.TC_score_missing is True
        assert stored.T_score_missing is False

    @pytest.mark.django_db
    def test_every_environmental_correction_writes_its_own_flag(self):
        corrections = {
            "S": "present_corrected",
            "E": "present_not_corrected",
            "TOPO": "present_not_significant",
            "PAL": "not_recognized",
            "SUR": "present_corrected",
            "CONV": "present_not_corrected",
            "HR": "present_corrected",
        }

        stored = self.reload(
            self.build_child(
                self.inputs_of("B2-not-considered"),
                uncertainty=5,
                corrections=corrections,
            )
        )

        assert stored.quality.endswith(".SeXxVcR")

    @pytest.mark.django_db
    def test_saving_a_correction_refreshes_its_child(self):
        from tests.factories import HeatFlowCorrectionFactory

        child = self.build_child(self.inputs_of("B3-no-in-situ-correction"))
        assert self.reload(child).M_score == "M1x"

        correction = HeatFlowCorrectionFactory(
            heat_flow=child, correction_type="IS", status="not_considered"
        )
        assert self.reload(child).M_score == "M1"

        correction.status = "present_corrected"
        correction.save()
        # Present and corrected is neither of the agreeing statuses for a corrected pT.
        assert self.reload(child).TC_score == pytest.approx(0.8)

    @pytest.mark.django_db
    def test_a_child_takes_the_bottom_water_waiver_from_its_own_correction(self):
        from heat_flow import vocabularies
        from tests.factories import (
            HeatFlowCorrectionFactory,
            HeatFlowFactory,
            HeatFlowIntervalFactory,
            HeatFlowSiteFactory,
            ProbeMetadataFactory,
            ThermalGradientFactory,
        )
        from tests.test_heat_flow.test_quality import concepts

        site = HeatFlowSiteFactory(explo_method="probing_offshore", elevation=-1000)
        interval = HeatFlowIntervalFactory(site=site)
        ProbeMetadataFactory(
            interval=interval, penetration=12, tilt=5, probe_type=[]
        )
        gradient = ThermalGradientFactory(
            sample=interval,
            number=6,
            method_top=concepts(vocabularies.TemperatureMethod),
            method_bottom=concepts(vocabularies.TemperatureMethod),
        )
        child = HeatFlowFactory(sample=interval, thermal_gradient=gradient)
        # 1.0, +0.1 penetration, +0.1 recordings, -0.2 water depth, 0 tilt.
        assert self.reload(child).T_score == pytest.approx(1.0)

        HeatFlowCorrectionFactory(
            heat_flow=child, correction_type="SUR", status="present_corrected"
        )

        assert self.reload(child).T_score == pytest.approx(1.2)
        # The gradient keeps the score that reads no child.
        assert type(gradient).objects.get(pk=gradient.pk).score == pytest.approx(1.0)

    @pytest.mark.django_db
    def test_deleting_a_correction_refreshes_its_child_on_commit(
        self, django_capture_on_commit_callbacks
    ):
        from tests.factories import HeatFlowCorrectionFactory

        child = self.build_child(self.inputs_of("B2-not-considered"))
        correction = HeatFlowCorrectionFactory(
            heat_flow=child, correction_type="HR", status="present_corrected"
        )
        assert self.reload(child).quality.endswith(".------R")

        with django_capture_on_commit_callbacks(execute=False) as callbacks:
            correction.delete()

        assert self.reload(child).quality.endswith(".------R")
        assert len(callbacks) == 1
        callbacks[0]()
        assert self.reload(child).quality.endswith(".-------")

    @pytest.mark.django_db
    def test_deleting_a_child_with_its_corrections_refreshes_nothing_that_is_gone(
        self, django_capture_on_commit_callbacks
    ):
        from heat_flow.models import HeatFlow
        from tests.factories import HeatFlowCorrectionFactory

        child = self.build_child(self.inputs_of("B2-not-considered"))
        for correction_type in ("S", "E", "SUR"):
            HeatFlowCorrectionFactory(
                heat_flow=child, correction_type=correction_type, status="-"
            )

        with django_capture_on_commit_callbacks(execute=True):
            child.delete()

        assert not HeatFlow.objects.filter(pk=child.pk).exists()

    @pytest.mark.django_db
    def test_a_query_on_a_corrected_score_returns_exactly_the_matching_children(
        self,
    ):
        from heat_flow.models import HeatFlow

        best = self.build_child(self.inputs_of("B2-not-considered"))
        worse = self.build_child(self.inputs_of("B6-tunnelling-literature"))
        worst = self.build_child(self.inputs_of("X4-single-point-plus-surface"))

        assert set(HeatFlow.objects.filter(T_score=1.1)) == {best}
        assert set(HeatFlow.objects.filter(T_score__lt=1.0)) == {worse, worst}
        assert set(HeatFlow.objects.filter(TC_score__lte=0.3)) == {worse, worst}
        assert set(HeatFlow.objects.filter(TC_score=0.8)) == {best}

    @pytest.mark.django_db
    def test_a_child_created_without_scores_carries_the_defaults_until_saved(self):
        from heat_flow.models import HeatFlow

        fresh = HeatFlow()

        assert fresh.T_score is None
        assert fresh.TC_score is None
        assert fresh.T_score_missing is False
        assert fresh.TC_score_missing is False
        assert fresh.quality_scheme == ""
        assert HeatFlow._meta.get_field("M_score").max_length >= len("M3x")

    @pytest.mark.parametrize(
        "field_name",
        [
            "U_score",
            "M_score",
            "quality",
            "T_score",
            "TC_score",
            "T_score_missing",
            "TC_score_missing",
            "quality_scheme",
        ],
    )
    def test_every_stored_score_is_calculated_and_documented_on_the_field(
        self, field_name
    ):
        from heat_flow.models import HeatFlow

        field = HeatFlow._meta.get_field(field_name)

        assert field.editable is False
        assert str(field.verbose_name).strip()
        assert str(field.help_text).strip()

    @pytest.mark.parametrize("name", ["get_quality", "get_perturbation_effects"])
    def test_the_2023_scoring_methods_are_gone(self, name):
        from heat_flow.models import HeatFlow

        assert not hasattr(HeatFlow, name)
