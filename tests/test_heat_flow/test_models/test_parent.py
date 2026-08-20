"""Tests for the site and the parent heat flow value.

Mirrors ``project/heat_flow/models/parent.py``.
"""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from fairdm.contrib.location.models import Point


class TestHeatFlowSite:
    @pytest.mark.django_db
    def test_heat_flow_site_persistence(self, dataset):
        """
        T005 – HeatFlowSite persists every field FR-001 lists and reads back
        with correct values and types, including an optional location FK
        (FR-001, FR-002, FR-003, SC-003).
        """
        from fairdm.contrib.location.models import Point
        from heat_flow.models import HeatFlowSite

        point = Point.objects.create(x=Decimal("8.5"), y=Decimal("47.4"))
        site = HeatFlowSite.objects.create(
            dataset=dataset,
            name="Schwarzwald Site",
            country="Germany",
            region="Baden-Württemberg",
            continent="Europe",
            domain="Rhine Graben",
            type="land",
            environment="onshore_continental",
            explo_method="drilling",
            location=point,
            elevation=350.0,
            elevation_datum="NAVD88",
            azimuth=90.0,
            inclination=85.0,
            length=1200.0,
        )
        site_db = HeatFlowSite.objects.get(pk=site.pk)

        assert site_db.name == "Schwarzwald Site"
        assert site_db.country == "Germany"
        assert site_db.region == "Baden-Württemberg"
        assert site_db.continent == "Europe"
        assert site_db.domain == "Rhine Graben"
        assert str(site_db.type) == "land"
        assert str(site_db.environment) == "onshore_continental"
        assert str(site_db.explo_method) == "drilling"
        assert site_db.location is not None
        assert site_db.location.x == Decimal("8.500000")
        assert site_db.location.y == Decimal("47.400000")

        assert hasattr(site_db.elevation, "magnitude")
        assert float(site_db.elevation.magnitude) == pytest.approx(350.0)
        assert str(site_db.elevation_datum) == "NAVD88"

        assert hasattr(site_db.azimuth, "magnitude")
        assert float(site_db.azimuth.magnitude) == pytest.approx(90.0)
        assert hasattr(site_db.inclination, "magnitude")
        assert float(site_db.inclination.magnitude) == pytest.approx(85.0)

        # "borehole depth" (FR-001) is the inherited GenericHole.length field,
        # exposed under that name via the total_depth_MD property.
        assert hasattr(site_db.length, "magnitude")
        assert float(site_db.length.magnitude) == pytest.approx(1200.0)
        assert float(site_db.total_depth_MD.magnitude) == pytest.approx(1200.0)

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


class TestHeatFlowSiteLocationUniqueness:
    """FR-004, FR-005, US-2 — a site is identified by its coordinate pair."""

    @pytest.mark.django_db
    def test_second_site_at_an_occupied_pair_is_refused(self, dataset):
        """
        T038 – A second HeatFlowSite saved at a coordinate pair another site
        already holds is refused via save(), and the error names the pair.
        """
        from heat_flow.models import HeatFlowSite

        point = Point.objects.create(x=Decimal("8.5"), y=Decimal("47.4"))
        HeatFlowSite.objects.create(dataset=dataset, name="First", location=point)

        with pytest.raises(ValidationError) as excinfo:
            second = HeatFlowSite(dataset=dataset, name="Second", location=point)
            second.save()

        message = str(excinfo.value)
        assert "8.5" in message
        assert "47.4" in message

    @pytest.mark.django_db
    def test_second_site_at_an_occupied_pair_is_refused_by_clean(self, dataset):
        """
        T045 – The rule also fires from clean(), so the admin reports a
        duplicate as a field error rather than a server error.
        """
        from heat_flow.models import HeatFlowSite

        point = Point.objects.create(x=Decimal("8.5"), y=Decimal("47.4"))
        HeatFlowSite.objects.create(dataset=dataset, name="First", location=point)

        second = HeatFlowSite(dataset=dataset, name="Second", location=point)
        with pytest.raises(ValidationError):
            second.clean()

    @pytest.mark.django_db
    def test_one_point_row_per_coordinate_pair(self):
        """
        T042 – The rule is written against ``location``, not against coordinate
        values, and that is only equivalent to "one site per coordinate pair"
        because the framework holds one Point row per pair.  This pins that
        assumption: if it ever stops holding, the site rule silently stops
        meaning what FR-004 says, and this is the test that would go red.
        """
        first, created = Point.objects.get_or_create(
            x=Decimal("8.5"), y=Decimal("47.4")
        )
        assert created

        second, created_again = Point.objects.get_or_create(
            x=Decimal("8.5"), y=Decimal("47.4")
        )
        assert not created_again
        assert second.pk == first.pk

    @pytest.mark.django_db
    def test_saving_an_existing_site_again_is_accepted(self, dataset):
        """
        T039 – Saving an already-stored site again does not trip the
        uniqueness rule against itself.
        """
        from heat_flow.models import HeatFlowSite

        point = Point.objects.create(x=Decimal("8.5"), y=Decimal("47.4"))
        site = HeatFlowSite.objects.create(
            dataset=dataset, name="Existing", location=point
        )

        site.name = "Existing, renamed"
        site.save()

        site.refresh_from_db()
        assert site.name == "Existing, renamed"

    @pytest.mark.django_db
    def test_two_sites_with_no_location_are_both_accepted(self, dataset):
        """
        T040 – The rule binds only where a location is set: two sites
        without coordinates are both accepted.
        """
        from heat_flow.models import HeatFlowSite

        first = HeatFlowSite.objects.create(dataset=dataset, name="No Location A")
        second = HeatFlowSite.objects.create(dataset=dataset, name="No Location B")

        assert HeatFlowSite.objects.filter(pk__in=[first.pk, second.pk]).count() == 2

    @pytest.mark.django_db
    def test_two_sites_a_few_metres_apart_are_both_accepted(self, dataset):
        """
        T041 – Coordinates are taken exactly as supplied: two distinct pairs
        a few metres apart are two sites, not one.
        """
        from heat_flow.models import HeatFlowSite

        point_a = Point.objects.create(x=Decimal("8.500000"), y=Decimal("47.400000"))
        point_b = Point.objects.create(x=Decimal("8.500010"), y=Decimal("47.400010"))

        first = HeatFlowSite.objects.create(
            dataset=dataset, name="Near A", location=point_a
        )
        second = HeatFlowSite.objects.create(
            dataset=dataset, name="Near B", location=point_b
        )

        assert HeatFlowSite.objects.filter(pk__in=[first.pk, second.pk]).count() == 2


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
    def test_parent_persists_uncertainty_flag_comment_id_and_quality(
        self, dataset, site_fixture
    ):
        """
        T054 – A ParentHeatFlow persists its uncertainty, its heat production
        correction flag, its comment, its published identifier (ghfdb_id) and
        its quality code (FR-010).
        """
        from heat_flow.models import ParentHeatFlow

        parent = ParentHeatFlow.objects.create(
            dataset=dataset,
            sample=site_fixture,
            name="Full Parent",
            value=70.0,
            uncertainty=5.0,
            corr_HP_flag=True,
            comment="A representative surface value.",
            ghfdb_id=12345,
            quality="A1B2C3D4E5F6G",
        )

        reloaded = ParentHeatFlow.objects.get(pk=parent.pk)

        assert hasattr(reloaded.uncertainty, "magnitude")
        assert float(reloaded.uncertainty.magnitude) == pytest.approx(5.0)
        assert reloaded.corr_HP_flag is True
        assert reloaded.comment == "A representative surface value."
        assert reloaded.ghfdb_id == 12345
        assert reloaded.quality == "A1B2C3D4E5F6G"

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
