# Tests for the heat flow list tables. Mirrors ``project/heat_flow/tables.py``.
#
# A site is a named location: an interval and its measurements are placed at their site
# and show its coordinates, and only to a viewer who may see the site (ADR 0023).

import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.gis.geos import Point
from django.test import RequestFactory
from django_tables2 import RequestConfig
from fairdm.factories import DatasetFactory
from fairdm.utils.choices import Visibility

from tests.factories import (
    HeatFlowIntervalFactory,
    HeatFlowSiteFactory,
    IntervalConductivityFactory,
)


def coordinates(table_class, queryset):
    """Render a table for a visitor and return each row's latitude and longitude.

    A cell left empty reads as None.
    """
    request = RequestFactory().get("/")
    request.user = AnonymousUser()
    table = RequestConfig(request).configure(table_class(data=queryset))
    return [
        tuple(
            None if cell == table.default else str(cell)
            for cell in (row.get_cell("latitude"), row.get_cell("longitude"))
        )
        for row in table.rows
    ]


@pytest.fixture
def public_site(db):
    dataset = DatasetFactory(visibility=Visibility.PUBLIC, published=True)
    return HeatFlowSiteFactory(dataset=dataset, location=Point(8.5, 47.4, srid=4326))


@pytest.fixture
def private_site(db):
    dataset = DatasetFactory(visibility=Visibility.PRIVATE, published=True)
    return HeatFlowSiteFactory(dataset=dataset, location=Point(9.5, 48.4, srid=4326))


@pytest.mark.django_db
class TestHeatFlowSiteTable:
    def test_a_site_shows_its_own_coordinates(self, public_site):
        from heat_flow.models import HeatFlowSite
        from heat_flow.tables import HeatFlowSiteTable

        assert coordinates(HeatFlowSiteTable, HeatFlowSite.objects.all()) == [
            ("47.4", "8.5")
        ]

    def test_a_site_the_viewer_may_not_see_shows_none(self, private_site):
        from heat_flow.models import HeatFlowSite
        from heat_flow.tables import HeatFlowSiteTable

        assert coordinates(HeatFlowSiteTable, HeatFlowSite.objects.all()) == [
            (None, None)
        ]

    def test_the_raw_location_is_not_a_column(self):
        from heat_flow.tables import HeatFlowSiteTable

        assert "location" not in HeatFlowSiteTable.base_columns


@pytest.mark.django_db
class TestHeatFlowIntervalTable:
    def test_an_interval_shows_its_sites_coordinates(self, public_site):
        from heat_flow.models import HeatFlowInterval
        from heat_flow.tables import HeatFlowIntervalTable

        HeatFlowIntervalFactory(dataset=public_site.dataset, site=public_site)

        assert coordinates(HeatFlowIntervalTable, HeatFlowInterval.objects.all()) == [
            ("47.4", "8.5")
        ]

    def test_an_interval_at_a_site_the_viewer_may_not_see_shows_none(
        self, public_site, private_site
    ):
        # The interval is public, the site it is placed at is not.
        from heat_flow.models import HeatFlowInterval
        from heat_flow.tables import HeatFlowIntervalTable

        HeatFlowIntervalFactory(dataset=public_site.dataset, site=private_site)

        assert coordinates(HeatFlowIntervalTable, HeatFlowInterval.objects.all()) == [
            (None, None)
        ]

    def test_listing_more_intervals_takes_no_more_queries(self, public_site):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext
        from heat_flow.models import HeatFlowInterval
        from heat_flow.tables import HeatFlowIntervalTable

        def queries_to_list():
            with CaptureQueriesContext(connection) as captured:
                coordinates(HeatFlowIntervalTable, HeatFlowInterval.objects.all())
            return len(captured)

        HeatFlowIntervalFactory(dataset=public_site.dataset, site=public_site)
        one = queries_to_list()
        for _ in range(4):
            site = HeatFlowSiteFactory(dataset=public_site.dataset)
            HeatFlowIntervalFactory(dataset=public_site.dataset, site=site)

        assert queries_to_list() == one


@pytest.mark.django_db
class TestIntervalConductivityTable:
    def test_a_conductivity_shows_the_coordinates_of_its_intervals_site(
        self, public_site
    ):
        from heat_flow.models import IntervalConductivity
        from heat_flow.tables import IntervalConductivityTable

        interval = HeatFlowIntervalFactory(
            dataset=public_site.dataset, site=public_site
        )
        IntervalConductivityFactory(dataset=public_site.dataset, sample=interval)

        assert coordinates(
            IntervalConductivityTable, IntervalConductivity.objects.all()
        ) == [("47.4", "8.5")]
