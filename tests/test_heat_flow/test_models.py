"""
Tests for heat_flow models – User Stories US1, US2, US3.

US1: Site and measurement data can be stored and retrieved (T013–T020, T053).
US2: Parent–child aggregation relationship is correctly modelled (T026–T029).
US3: Marine probe measurements have supplementary metadata (T035–T038).
"""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError


class TestHeatFlowSite:
    @pytest.mark.django_db
    def test_heat_flow_site_persistence(self, dataset):
        """
        T013 – HeatFlowSite can be saved and reloaded with all scalar fields intact,
        including an optional location FK (FR-002, FR-003, SC-003).
        """
        from fairdm.contrib.location.models import Point
        from heat_flow.models import HeatFlowSite

        point = Point.objects.create(x=Decimal("8.5"), y=Decimal("47.4"))
        site = HeatFlowSite.objects.create(
            dataset=dataset,
            name="Schwarzwald Site",
            country="Germany",
            continent="Europe",
            environment="onshore_continental",
            explo_method="drilling",
            location=point,
        )
        site_db = HeatFlowSite.objects.get(pk=site.pk)

        assert site_db.name == "Schwarzwald Site"
        assert site_db.country == "Germany"
        assert site_db.continent == "Europe"
        assert str(site_db.environment) == "onshore_continental"
        assert str(site_db.explo_method) == "drilling"
        assert site_db.location is not None
        assert site_db.location.x == Decimal("8.500000")
        assert site_db.location.y == Decimal("47.400000")

    @pytest.mark.django_db
    def test_heat_flow_site_explo_purpose_m2m(self, dataset):
        """
        T013 – explo_purpose M2M relationship can be added and reloaded (FR-003, H2).
        """
        from heat_flow.models import HeatFlowSite
        from research_vocabs.models import Concept, Vocabulary

        site = HeatFlowSite.objects.create(dataset=dataset, name="M2M Site")
        vocab, _ = Vocabulary.objects.get_or_create(name="exploration-purpose")
        concept, _ = Concept.objects.get_or_create(vocabulary=vocab, name="research")
        site.explo_purpose.add(concept)

        reloaded = HeatFlowSite.objects.get(pk=site.pk)
        assert reloaded.explo_purpose.count() == 1


class TestHeatFlowInterval:
    def test_site_fk_is_named_site_and_targets_heat_flow_site(self):
        """
        The interval-to-site link is called ``site`` and is typed against
        ``HeatFlowSite``, not the polymorphic ``Sample`` root.  "Parent" and
        "child" are reserved for the relationship between measurements, so no
        part of this field may borrow either word.
        """
        from heat_flow.models import HeatFlowInterval, HeatFlowSite

        field = HeatFlowInterval._meta.get_field("site")
        assert field.related_model is HeatFlowSite
        assert field.remote_field.related_name == "intervals"
        assert "parent" not in str(field.verbose_name).lower()

    @pytest.mark.django_db
    def test_interval_links_to_site(self, dataset, site_fixture):
        """
        T014 – HeatFlowInterval.site FK resolves to site; reverse 'intervals'
        accessor works (US1 scenario 2, A9).
        """
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
        """
        T015 – ThermalGradient and IntervalConductivity link to interval and appear
        in interval.measurements; Pint Quantity attributes present on value and depth
        fields (FR-006, A5, US1 scenario 3).
        """
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
        """
        T053 – HeatFlowInterval.full_clean() raises ValidationError when
        top >= bottom (EC-001, M4).
        """
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
        """
        T053 – HeatFlowInterval.full_clean() passes when bottom > top (EC-001).
        """
        from heat_flow.models import HeatFlowInterval

        interval = HeatFlowInterval(
            dataset=dataset,
            site=site_fixture,
            name="Valid Interval",
            top=0,
            bottom=500,
        )
        interval.full_clean()  # must not raise


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
        """
        T016 – Forward and reverse FK relationships on HeatFlow child resolve
        correctly; default US/MS score values are Ux/Mx on a fresh instance
        (FR-014, A11, US1 scenario 4).
        """
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
    def test_heat_flow_save_rejects_wrong_sample(self, site_fixture, child_fixture):
        """
        T018 – HeatFlow.save() raises ValidationError when sample is a
        HeatFlowSite (wrong type); only HeatFlowInterval is valid (FR-010a).
        """
        with pytest.raises(ValidationError):
            child_fixture.sample = site_fixture
            child_fixture.save()

    @pytest.mark.django_db
    def test_multiple_heatflow_can_share_gradient(
        self, dataset, interval_fixture, gradient_fixture, parent_fixture
    ):
        """
        T020 – Two HeatFlow children may reference the same ThermalGradient FK
        without IntegrityError (FR-013 / R5).
        """
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
    def test_heat_flow_allows_null_gradient_and_conductivity(
        self, dataset, interval_fixture
    ):
        """
        T020 – A HeatFlow with neither gradient nor conductivity is valid; incomplete
        records must not be blocked at entry time (EC-002, M2).
        """
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
        """
        T038 – HeatFlow.is_probe is True when the linked interval has probe
        metadata; False otherwise (US3 independent test).
        """
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
        """
        T017 – HeatFlowCorrection records link via FK and are accessible via
        child.corrections (US1 scenario 5).
        """
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
        """
        T057 – IS + tilt_corrected is a valid combination; save() must not raise (FR-021).
        """
        from heat_flow.models import HeatFlowCorrection

        corr = HeatFlowCorrection(
            heat_flow=child_fixture, correction_type="IS", status="tilt_corrected"
        )
        corr.save()  # must not raise
        assert corr.pk is not None

    @pytest.mark.django_db
    def test_correction_invalid_status_rejected(self, child_fixture):
        """
        T057 – Invalid status/type combinations raise ValidationError from save() (FR-021):
          - IS + considered_p (considered_p only valid for environmental types)
          - S + tilt_corrected (tilt_corrected only valid for IS)
          - T + present_not_significant (present_not_significant is environmental only)
        """
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
        """
        T057 – The unspecified status ("-") is accepted for any correction type (FR-021).
        """
        from heat_flow.models import HeatFlowCorrection

        for ct in ["IS", "T", "S", "E", "TOPO", "PAL", "SUR", "CONV", "HR"]:
            corr = HeatFlowCorrection(
                heat_flow=child_fixture, correction_type=ct, status="-"
            )
            corr.save()  # must not raise

    @pytest.mark.django_db
    def test_correction_invalid_type_rejected(self, child_fixture):
        """
        T057 – A correction with an unrecognised correction_type is rejected by Django's
        field-level choices validation when full_clean() is called (EC-004, L1).
        """
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
        """
        T018 – ThermalGradient.save() raises ValidationError when sample is a
        HeatFlowSite (FR-016a).
        """
        with pytest.raises(ValidationError):
            gradient_fixture.sample = site_fixture
            gradient_fixture.save()

    @pytest.mark.django_db
    def test_value_non_nullable_thermal_gradient(self, dataset, interval_fixture):
        """
        T019 – ThermalGradient.value is non-nullable; omitting it raises an
        IntegrityError at the database layer (R3).
        """
        from heat_flow.models import ThermalGradient

        with pytest.raises((IntegrityError, ValidationError)):
            ThermalGradient.objects.create(
                dataset=dataset, sample=interval_fixture, name="No Value"
            )


class TestIntervalConductivity:
    @pytest.mark.django_db
    def test_interval_conductivity_save_rejects_wrong_sample(
        self, site_fixture, conductivity_fixture
    ):
        """
        T018 – IntervalConductivity.save() raises ValidationError when sample is a
        HeatFlowSite (FR-018a).
        """
        with pytest.raises(ValidationError):
            conductivity_fixture.sample = site_fixture
            conductivity_fixture.save()

    @pytest.mark.django_db
    def test_value_non_nullable_interval_conductivity(self, dataset, interval_fixture):
        """
        T019 – IntervalConductivity.value is non-nullable; omitting it raises an
        IntegrityError at the database layer (R3).
        """
        from heat_flow.models import IntervalConductivity

        with pytest.raises((IntegrityError, ValidationError)):
            IntervalConductivity.objects.create(
                dataset=dataset, sample=interval_fixture, name="No Value"
            )


class TestParentHeatFlow:
    def test_table_name_follows_the_owning_application(self):
        """
        ``ParentHeatFlow`` lives in ``heat_flow``, so its table is named for
        ``heat_flow``.  The old ``ghfdb_`` name came from a move into the
        ``ghfdb`` application that was abandoned (docs/adr/0001).
        """
        from heat_flow.models import ParentHeatFlow

        assert ParentHeatFlow._meta.db_table == "heat_flow_parentheatflow"

    @pytest.mark.django_db
    def test_parent_children_aggregation(self, dataset, site_fixture, interval_fixture):
        """
        T026 – ParentHeatFlow.children reverse relation returns correct counts;
        is_relevant filter works (US2 scenarios 1–2).
        """
        from heat_flow.models import HeatFlow, ParentHeatFlow

        parent = ParentHeatFlow.objects.create(
            dataset=dataset, sample=site_fixture, name="P", value=70.0
        )
        HeatFlow.objects.create(
            dataset=dataset,
            sample=interval_fixture,
            name="C1",
            value=65.0,
            parent=parent,
            is_relevant=True,
        )
        HeatFlow.objects.create(
            dataset=dataset,
            sample=interval_fixture,
            name="C2",
            value=68.0,
            parent=parent,
            is_relevant=True,
        )
        HeatFlow.objects.create(
            dataset=dataset,
            sample=interval_fixture,
            name="C3",
            value=72.0,
            parent=parent,
            is_relevant=False,
        )

        assert parent.children.count() == 3
        assert parent.children.filter(is_relevant=True).count() == 2

    @pytest.mark.django_db
    def test_parent_delete_sets_child_null(self, dataset, site_fixture, interval_fixture):
        """
        T027 – Deleting a ParentHeatFlow sets child.parent_id to NULL via SET_NULL
        (US2 scenario 3, SC-004).
        """
        from heat_flow.models import HeatFlow, ParentHeatFlow

        parent = ParentHeatFlow.objects.create(
            dataset=dataset, sample=site_fixture, name="P", value=70.0
        )
        child = HeatFlow.objects.create(
            dataset=dataset, sample=interval_fixture, name="C", value=65.0, parent=parent
        )
        child_pk = child.pk

        parent.delete()

        reloaded = HeatFlow.objects.get(pk=child_pk)
        assert reloaded.parent_id is None

    @pytest.mark.django_db
    def test_unique_parent_per_site_app_level(self, dataset, site_fixture):
        """
        T028 – Creating a second ParentHeatFlow for the same HeatFlowSite via
        .save() raises ValidationError from the app-layer uniqueness guard (H1).
        """
        from heat_flow.models import ParentHeatFlow

        ParentHeatFlow.objects.create(
            dataset=dataset, sample=site_fixture, name="First", value=70.0
        )
        with pytest.raises(ValidationError):
            second = ParentHeatFlow(
                dataset=dataset, sample=site_fixture, name="Second", value=75.0
            )
            second.save()

    @pytest.mark.django_db
    def test_unique_parent_per_site_db_level(self, dataset, site_fixture):
        """
        T028 – DB-level unique enforcement requires a UniqueConstraint on `sample`.
        NOTE: This constraint cannot be added to ParentHeatFlow.Meta because `sample_id`
        is a column on the base `measurement` table (MTI), not on `heat_flow_parentheatflow`.
        SQLite treats the reference as an expression and raises OperationalError on table
        creation.  Uniqueness is enforced at app level by ParentHeatFlow.save() instead.
        This test is marked xfail to document the architectural limitation.
        """
        # App-level enforcement is validated in test_unique_parent_per_site_app_level
        pytest.skip(
            "DB-level UniqueConstraint not viable with polymorphic MTI + SQLite (column lives on base table)"
        )

    @pytest.mark.django_db
    def test_parent_with_zero_children_is_valid(self, dataset, site_fixture):
        """
        T028 – A ParentHeatFlow with no children is valid (edge case from spec).
        """
        from heat_flow.models import ParentHeatFlow

        parent = ParentHeatFlow.objects.create(
            dataset=dataset, sample=site_fixture, name="Childless", value=70.0
        )
        assert parent.children.count() == 0

    @pytest.mark.django_db
    def test_parent_save_rejects_wrong_sample(
        self, dataset, interval_fixture, parent_fixture
    ):
        """
        T029 – ParentHeatFlow.save() raises ValidationError when sample is a
        HeatFlowInterval rather than HeatFlowSite (FR-008a).
        """
        with pytest.raises(ValidationError):
            parent_fixture.sample = interval_fixture
            parent_fixture.save()


class TestProbeMetadata:
    @pytest.mark.django_db
    def test_probe_metadata_linked_to_interval(
        self, dataset, site_fixture, interval_fixture
    ):
        """
        T035 – ProbeMetadata can be created for an interval; all fields readable
        via interval.probe_metadata (US3 scenario 1).
        """
        from heat_flow.models import ProbeMetadata

        ProbeMetadata.objects.create(
            interval=interval_fixture,
            penetration=3.5,
            length=5.0,
            tilt=2.0,
        )
        reloaded = type(interval_fixture).objects.get(pk=interval_fixture.pk)
        assert float(reloaded.probe_metadata.penetration.magnitude) == pytest.approx(3.5)
        assert float(reloaded.probe_metadata.length.magnitude) == pytest.approx(5.0)
        assert float(reloaded.probe_metadata.tilt.magnitude) == pytest.approx(2.0)

    @pytest.mark.django_db
    def test_interval_without_probe_raises(self, dataset, site_fixture):
        """
        T036 – Accessing probe_metadata on an interval with none raises
        RelatedObjectDoesNotExist (US3 scenario 2).
        """
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
        """
        T037 – Deleting the interval also deletes its ProbeMetadata (CASCADE;
        US3 scenario 3, SC-004).
        """
        from heat_flow.models import ProbeMetadata

        probe = ProbeMetadata.objects.create(interval=interval_fixture, penetration=3.5)
        probe_pk = probe.pk
        interval_fixture.delete()
        assert not ProbeMetadata.objects.filter(pk=probe_pk).exists()
