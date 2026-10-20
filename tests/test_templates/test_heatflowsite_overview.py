# Tests for the site's overview page, read through its URL. The page's content is found
# by the ``data-`` hooks its templates carry, never by wording. Mirrors no Python
# module: the subject is the templates under ``project/heat_flow/templates/`` and
# ``templates/cotton/``, declared under ``non-mirror-paths`` in pyproject.toml.

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from fairdm.contrib.contributors.choices import ContributionLevel
from fairdm.factories import ContributionFactory, PersonFactory
from heat_flow.models import HeatFlowSite, ParentHeatFlow
from heat_flow.overview import HeatFlowPage

from tests.factories import (
    HeatFlowFactory,
    HeatFlowIntervalFactory,
    HeatFlowSiteFactory,
)

pytestmark = pytest.mark.django_db

SHOW_ALL = "?show=all#intervals"
ACCESS_FIELDS = (
    "top",
    "bottom",
    "length",
    "vertical_depth",
    "inclination",
    "azimuth",
    "elevation",
    "elevation_datum",
)
LOCATION_FIELDS = ("country", "region", "continent", "domain")


def link_to(node, record):
    """Say whether ``node`` links to ``record``'s page."""
    return record.get_absolute_url() in node.hrefs


def term(concept):
    """A vocabulary concept's label in English, as a graph concept gives it as a method.

    The page capitalises a label's first letter, so compare it ignoring case.
    """
    label = concept.label
    return str(label("en") if callable(label) else label)


def add_interval(site, top, bottom, dataset, children=0):
    """Add an interval to ``site`` with ``children`` heat flow values over it."""
    interval = HeatFlowIntervalFactory(
        dataset=dataset, site=site, top=top, bottom=bottom
    )
    kids = [HeatFlowFactory(dataset=dataset, sample=interval) for _ in range(children)]
    return interval, kids


def listed(page):
    """The intervals the page lists, in the order it lists them, by primary key."""
    rows = page.find("data-heat-flow", "intervals").find_all("data-interval")
    return [int(row.attrs["data-interval"]) for row in rows]


@pytest.fixture
def site_only(published_dataset):
    """A site with no parent and no intervals."""
    return HeatFlowSiteFactory(dataset=published_dataset)


@pytest.fixture
def small_cut(monkeypatch):
    """Cut a site's interval list at two."""
    monkeypatch.setattr(HeatFlowPage, "intervals_shown", 2)


class TestSitePage:
    def test_it_shows_the_parent_with_its_quality_code_linked_to_its_page(
        self, document, page_records
    ):
        parent = page_records["parent"]
        parent.refresh_from_db()

        page = document(page_records["site"])

        node = page.find("data-heat-flow", "parent")
        assert "data-state" not in node.attrs
        assert link_to(node, parent)
        assert str(parent.print_value()) in node.text
        assert node.find("data-quality", "code").attrs["data-value"] == (
            parent.quality or ""
        )

    def test_a_site_with_no_parent_says_none_is_designated(
        self, document, page_records
    ):
        ParentHeatFlow.objects.filter(pk=page_records["parent"].pk).delete()

        page = document(page_records["site"])

        assert page.find("data-heat-flow", "parent").attrs["data-state"] == "none"

    def test_it_lists_the_intervals_from_shallowest_to_deepest_each_linked(
        self, document, page_records, published_dataset
    ):
        site = page_records["site"]
        deep, _ = add_interval(site, 300, 400, published_dataset)
        wide, _ = add_interval(site, 100, 900, published_dataset)
        narrow, _ = add_interval(site, 100, 200, published_dataset)

        page = document(site)

        assert listed(page) == [
            page_records["interval"].pk,
            narrow.pk,
            wide.pk,
            deep.pk,
        ]
        intervals = page.find("data-heat-flow", "intervals")
        for interval in (page_records["interval"], narrow, wide, deep):
            assert link_to(intervals, interval)

    def test_it_lists_each_interval_with_the_children_determined_over_it_linked(
        self, document, page_records, published_dataset
    ):
        site = page_records["site"]
        other, kids = add_interval(site, 600, 700, published_dataset, children=2)

        page = document(site)

        intervals = page.find("data-heat-flow", "intervals")
        rows = {
            int(row.attrs["data-interval"]): row
            for row in intervals.find_all("data-interval")
        }
        assert {
            int(c.attrs["data-child"]) for c in rows[other.pk].find_all("data-child")
        } == {kid.pk for kid in kids}
        for kid in kids:
            assert link_to(rows[other.pk], kid)
        assert link_to(rows[page_records["interval"].pk], page_records["child"])

    def test_it_shows_each_childs_quality_code(self, document, page_records):
        child = page_records["child"]
        child.refresh_from_db()

        page = document(page_records["site"])

        row = page.find("data-heat-flow", "intervals").find("data-child", str(child.pk))
        assert row.find("data-quality", "code").attrs["data-value"] == (
            child.quality or ""
        )

    def test_an_interval_with_no_children_says_so(
        self, document, page_records, published_dataset
    ):
        empty, _ = add_interval(page_records["site"], 600, 700, published_dataset)

        page = document(page_records["site"])

        row = page.find("data-interval", str(empty.pk))
        assert row.find_all("data-child") == []
        assert row.attrs["data-state"] == "empty"

    def test_a_site_with_no_intervals_says_none_are_recorded(self, document, site_only):
        page = document(site_only)

        assert page.find("data-heat-flow", "intervals").attrs["data-state"] == "empty"

    def test_it_shows_the_environment_method_and_purpose_as_vocabulary_terms(
        self, document, page_records
    ):
        site = page_records["site"]
        site.refresh_from_db()
        purpose = site.explo_purpose.first()

        page = document(site)

        assert term(site.environment).casefold() in (
            page.find("data-field", "environment").text.casefold()
        )
        assert term(site.explo_method).casefold() in (
            page.find("data-field", "explo_method").text.casefold()
        )
        assert term(purpose).casefold() in (
            page.find("data-field", "explo_purpose").text.casefold()
        )

    def test_it_shows_the_access_geometry_and_where_it_lies(
        self, document, page_records
    ):
        HeatFlowSite.objects.filter(pk=page_records["site"].pk).update(
            country="Germany", azimuth=None
        )

        page = document(page_records["site"])

        for name in (*ACCESS_FIELDS, *LOCATION_FIELDS):
            assert page.find("data-field", name) is not None
        assert "Germany" in page.find("data-field", "country").text
        assert "data-state" not in page.find("data-field", "country").attrs
        assert page.find("data-field", "azimuth").attrs["data-state"] == "not-recorded"


class TestSitePageCutList:
    def test_it_shows_the_cut_and_says_how_many_more(
        self, document, page_records, published_dataset, small_cut
    ):
        for top in (100, 200, 300):
            add_interval(page_records["site"], top, top + 50, published_dataset)

        page = document(page_records["site"])

        intervals = page.find("data-heat-flow", "intervals")
        assert len(listed(page)) == 2
        assert intervals.attrs["data-more"] == "2"

    def test_it_links_to_the_same_page_asking_for_all_of_them(
        self, document, page_records, published_dataset, small_cut
    ):
        for top in (100, 200, 300):
            add_interval(page_records["site"], top, top + 50, published_dataset)

        page = document(page_records["site"])

        assert SHOW_ALL in page.find("data-heat-flow", "intervals").hrefs

    def test_show_all_lists_every_interval_and_drops_the_link(
        self, document, page_records, published_dataset, small_cut
    ):
        for top in (100, 200, 300):
            add_interval(page_records["site"], top, top + 50, published_dataset)

        page = document(page_records["site"], show="all")

        intervals = page.find("data-heat-flow", "intervals")
        assert len(listed(page)) == 4
        assert "data-more" not in intervals.attrs
        assert SHOW_ALL not in intervals.hrefs

    def test_a_site_within_the_cut_has_no_remainder(self, document, page_records):
        page = document(page_records["site"])

        intervals = page.find("data-heat-flow", "intervals")
        assert "data-more" not in intervals.attrs
        assert SHOW_ALL not in intervals.hrefs


class TestSitePageForARecordTheVisitorMayNotOpen:
    def test_a_hidden_interval_is_counted_and_never_linked(
        self, document, page_records, published_dataset, hide
    ):
        concealed, _ = add_interval(page_records["site"], 600, 700, published_dataset)
        hide(concealed)

        page = document(page_records["site"])

        intervals = page.find("data-heat-flow", "intervals")
        assert intervals.attrs["data-hidden"] == "1"
        assert concealed.pk not in listed(page)
        assert concealed.get_absolute_url() not in page.root.hrefs

    def test_a_hidden_child_is_counted_against_its_interval_and_never_linked(
        self, document, page_records, hide
    ):
        concealed = HeatFlowFactory(
            dataset=page_records["child"].dataset, sample=page_records["interval"]
        )
        hide(concealed)

        page = document(page_records["site"])

        row = page.find("data-interval", str(page_records["interval"].pk))
        assert row.attrs["data-hidden"] == "1"
        assert link_to(row, page_records["child"])
        assert concealed.get_absolute_url() not in page.root.hrefs

    def test_an_interval_whose_children_are_all_hidden_is_not_said_to_be_empty(
        self, document, page_records, hide
    ):
        hide(page_records["child"])

        page = document(page_records["site"])

        row = page.find("data-interval", str(page_records["interval"].pk))
        assert row.attrs["data-hidden"] == "1"
        assert "data-state" not in row.attrs

    def test_a_hidden_parent_is_neither_named_nor_linked(
        self, document, page_records, hide
    ):
        hide(page_records["parent"])

        page = document(page_records["site"])

        node = page.find("data-heat-flow", "parent")
        assert node.attrs["data-state"] == "hidden"
        assert not link_to(node, page_records["parent"])
        assert str(page_records["parent"].print_value()) not in node.text
        assert page_records["parent"].get_absolute_url() not in page.root.hrefs

    def test_a_member_of_the_dataset_is_shown_the_hidden_parent(
        self, document, page_records, hide, member
    ):
        hide(page_records["parent"])

        page = document(page_records["site"], user=member)

        node = page.find("data-heat-flow", "parent")
        assert "data-state" not in node.attrs
        assert link_to(node, page_records["parent"])


class TestSitePageKeepsFairDMsPage:
    def test_it_keeps_the_identifiers_and_citation_cards(self, document, page_records):
        page = document(page_records["site"])

        assert page.find("data-card", "identifiers") is not None
        assert page.find("data-card", "citation") is not None

    def test_a_dataset_manager_is_shown_the_manage_menu(self, document, page_records):
        manager = PersonFactory(is_claimed=True, password="test-pass-123")
        ContributionFactory(
            contributor=manager,
            content_object=page_records["site"].dataset,
            level=ContributionLevel.MANAGE,
        )

        page = document(page_records["site"], user=manager)

        assert page.find("data-menu", "manage") is not None

    def test_a_visitor_is_not_shown_the_manage_menu(self, document, page_records):
        assert document(page_records["site"]).find("data-menu", "manage") is None


class TestSitePageQueries:
    def test_the_page_makes_the_same_queries_for_one_interval_and_for_three(
        self, client, page_records, published_dataset
    ):
        site = page_records["site"]
        url = site.get_absolute_url()

        def count():
            with CaptureQueriesContext(connection) as queries:
                assert client.get(url).status_code == 200
            return len(queries)

        count()
        with_one = count()
        for top in (300, 400):
            add_interval(site, top, top + 50, published_dataset, children=2)

        with_three = count()

        assert with_three == with_one
