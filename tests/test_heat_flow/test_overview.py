# Tests for the heat flow overview pages' gathering class. Mirrors
# ``project/heat_flow/overview.py``.

import pytest
from django.contrib.auth.models import AnonymousUser
from heat_flow.models import (
    HeatFlow,
    HeatFlowInterval,
    HeatFlowSite,
    IntervalConductivity,
    ParentHeatFlow,
    ThermalGradient,
)
from heat_flow.overview import HeatFlowPage
from heat_flow.quality import SCHEME_REVISION

from tests.factories import HeatFlowCorrectionFactory, HeatFlowFactory

pytestmark = pytest.mark.django_db


def hide(record, dataset):
    """Move a record into another dataset, as the database holds it."""
    type(record).objects.filter(pk=record.pk).update(dataset=dataset)
    record.refresh_from_db()


@pytest.fixture
def visitor():
    return AnonymousUser()


class TestHeatFlowPageOpens:
    def test_a_visitor_opens_a_record_in_a_published_dataset(
        self, page_records, visitor
    ):
        page = HeatFlowPage(page_records["child"], visitor)

        assert page.opens(page_records["gradient"]) is True

    def test_a_visitor_does_not_open_a_record_in_an_unpublished_dataset(
        self, page_records, unpublished_dataset, visitor
    ):
        hide(page_records["gradient"], unpublished_dataset)

        page = HeatFlowPage(page_records["child"], visitor)

        assert page.opens(page_records["gradient"]) is False

    def test_a_member_of_the_dataset_opens_its_unpublished_record(
        self, page_records, unpublished_dataset, member
    ):
        hide(page_records["gradient"], unpublished_dataset)

        page = HeatFlowPage(page_records["child"], member)

        assert page.opens(page_records["gradient"]) is True

    def test_nothing_opens_for_a_record_that_is_not_there(self, page_records, visitor):
        page = HeatFlowPage(page_records["child"], visitor)

        assert page.opens(None) is False


class TestHeatFlowPageSplit:
    def test_it_returns_the_records_the_visitor_may_open_and_counts_the_rest(
        self, page_records, unpublished_dataset, visitor
    ):
        hide(page_records["conductivity"], unpublished_dataset)
        records = [page_records["gradient"], page_records["conductivity"]]

        shown, hidden = HeatFlowPage(page_records["child"], visitor).split(records)

        assert shown == [page_records["gradient"]]
        assert hidden == 1

    def test_it_keeps_the_order_it_was_given(self, page_records, visitor):
        records = [page_records["conductivity"], page_records["gradient"]]

        shown, hidden = HeatFlowPage(page_records["child"], visitor).split(records)

        assert shown == records
        assert hidden == 0

    def test_it_makes_one_query_for_any_number_of_records(
        self, page_records, published_dataset, visitor, django_assert_num_queries
    ):
        page = HeatFlowPage(page_records["child"], visitor)
        many = [
            HeatFlowFactory(dataset=published_dataset, sample=page_records["interval"])
            for _ in range(4)
        ]

        with django_assert_num_queries(1):
            shown, hidden = page.split(many)

        assert (len(shown), hidden) == (4, 0)

    def test_it_makes_no_query_for_no_records(
        self, page_records, visitor, django_assert_num_queries
    ):
        page = HeatFlowPage(page_records["child"], visitor)

        with django_assert_num_queries(0):
            assert page.split([]) == ([], 0)

    def test_it_reads_samples_and_measurements_by_their_own_rule(
        self, page_records, unpublished_dataset, visitor
    ):
        hide(page_records["interval"], unpublished_dataset)

        page = HeatFlowPage(page_records["child"], visitor)

        assert page.split([page_records["interval"]]) == ([], 1)
        assert page.split([page_records["gradient"]]) == ([page_records["gradient"]], 0)


class TestHeatFlowPageIsStale:
    def test_the_current_scheme_revision_is_not_stale(self, page_records):
        child = page_records["child"]
        child.quality_scheme = SCHEME_REVISION

        assert HeatFlowPage.is_stale(child) is False

    def test_an_older_scheme_revision_is_stale(self, page_records):
        child = page_records["child"]
        child.quality_scheme = "hfqa_tool 0.1"

        assert HeatFlowPage.is_stale(child) is True

    def test_a_record_that_has_not_been_scored_is_not_stale(self, page_records):
        child = page_records["child"]
        child.quality_scheme = ""

        assert HeatFlowPage.is_stale(child) is False


class TestHeatFlowPageSiteLocation:
    def test_a_child_shows_the_location_of_its_intervals_site(
        self, page_records, visitor
    ):
        site = page_records["site"]

        place = HeatFlowPage(page_records["child"], visitor).site_location()

        assert place["visible"] is True
        assert place["site"] == site
        assert place["point"] == site.location

    def test_an_interval_shows_the_location_of_its_site(self, page_records, visitor):
        place = HeatFlowPage(page_records["interval"], visitor).site_location()

        assert place["point"] == page_records["site"].location

    def test_a_site_the_visitor_may_not_open_gives_no_location(
        self, page_records, unpublished_dataset, visitor
    ):
        hide(page_records["site"], unpublished_dataset)

        place = HeatFlowPage(page_records["child"], visitor).site_location()

        assert place["visible"] is False
        assert place["site"] is None
        assert place["point"] is None

    def test_a_site_without_a_location_is_visible_with_no_point(
        self, page_records, visitor
    ):
        HeatFlowSite.objects.filter(pk=page_records["site"].pk).update(location=None)
        child = HeatFlow.objects.get(pk=page_records["child"].pk)

        place = HeatFlowPage(child, visitor).site_location()

        assert place["visible"] is True
        assert place["point"] is None


class TestHeatFlowPageContext:
    @pytest.mark.parametrize(
        "model",
        [
            HeatFlowSite,
            HeatFlowInterval,
            HeatFlow,
            ThermalGradient,
            IntervalConductivity,
            ParentHeatFlow,
        ],
    )
    def test_it_gathers_a_page_for_every_heat_flow_type(
        self, page_records, visitor, model
    ):
        record = next(r for r in page_records.values() if type(r) is model)

        context = HeatFlowPage(record, visitor).context()

        assert isinstance(context, dict)

    def test_a_child_is_gathered_by_for_child(self, page_records, visitor):
        page = HeatFlowPage(page_records["child"], visitor)

        assert page.context() == page.for_child()


class TestHeatFlowPageForChild:
    def test_it_returns_every_related_record_the_visitor_may_open(
        self, page_records, visitor
    ):
        context = HeatFlowPage(page_records["child"], visitor).for_child()

        assert context["gradient"] == page_records["gradient"]
        assert context["conductivity"] == page_records["conductivity"]
        assert context["parent"] == page_records["parent"]
        assert context["interval"] == page_records["interval"]
        assert context["site"] == page_records["site"]
        assert context["gradient_hidden"] is False
        assert context["conductivity_hidden"] is False
        assert context["parent_hidden"] is False

    def test_it_returns_the_corrections_recorded_for_the_child(
        self, page_records, visitor
    ):
        child = page_records["child"]
        recorded = [
            HeatFlowCorrectionFactory(
                heat_flow=child, correction_type=kind, status="present_corrected"
            )
            for kind in ("S", "E")
        ]

        context = HeatFlowPage(child, visitor).for_child()

        assert set(context["corrections"]) == set(recorded)

    def test_a_child_with_nothing_related_gets_none_and_no_hidden_marks(
        self, page_records, visitor
    ):
        child = page_records["child"]
        HeatFlow.objects.filter(pk=child.pk).update(
            thermal_gradient=None, thermal_conductivity=None, parent=None
        )
        child.refresh_from_db()

        context = HeatFlowPage(child, visitor).for_child()

        assert context["gradient"] is None
        assert context["conductivity"] is None
        assert context["parent"] is None
        assert context["corrections"] == []
        assert context["gradient_hidden"] is False
        assert context["conductivity_hidden"] is False
        assert context["parent_hidden"] is False

    @pytest.mark.parametrize("name", ["gradient", "conductivity", "parent"])
    def test_a_record_in_an_unpublished_dataset_is_marked_hidden_and_not_returned(
        self, page_records, unpublished_dataset, visitor, name
    ):
        hide(page_records[name], unpublished_dataset)

        context = HeatFlowPage(page_records["child"], visitor).for_child()

        assert context[name] is None
        assert context[f"{name}_hidden"] is True

    def test_the_interval_and_site_in_an_unpublished_dataset_are_not_returned(
        self, page_records, unpublished_dataset, visitor
    ):
        hide(page_records["interval"], unpublished_dataset)
        hide(page_records["site"], unpublished_dataset)

        context = HeatFlowPage(page_records["child"], visitor).for_child()

        assert context["interval"] is None
        assert context["site"] is None
        assert context["location"]["visible"] is False

    def test_a_member_is_given_the_unpublished_records(
        self, page_records, unpublished_dataset, member
    ):
        hide(page_records["gradient"], unpublished_dataset)

        context = HeatFlowPage(page_records["child"], member).for_child()

        assert context["gradient"] == page_records["gradient"]
        assert context["gradient_hidden"] is False

    def test_it_says_whether_the_childs_scores_are_stale(self, page_records, visitor):
        child = page_records["child"]
        HeatFlow.objects.filter(pk=child.pk).update(quality_scheme="hfqa_tool 0.1")
        child.refresh_from_db()

        assert HeatFlowPage(child, visitor).for_child()["stale"] is True
