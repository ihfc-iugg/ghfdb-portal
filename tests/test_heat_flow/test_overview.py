# Tests for the heat flow overview pages' gathering class. Mirrors
# ``project/heat_flow/overview.py``.

import pytest
from django.contrib.auth.models import AnonymousUser
from django.db import connection
from django.test.utils import CaptureQueriesContext
from fairdm.core.sample.models import SampleIdentifier
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

from tests.factories import (
    HeatFlowCorrectionFactory,
    HeatFlowFactory,
    HeatFlowIntervalFactory,
    ProbeMetadataFactory,
)

pytestmark = pytest.mark.django_db


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
        self, page_records, hide, visitor
    ):
        hide(page_records["gradient"])

        page = HeatFlowPage(page_records["child"], visitor)

        assert page.opens(page_records["gradient"]) is False

    def test_a_member_of_the_dataset_opens_its_unpublished_record(
        self, page_records, hide, member
    ):
        hide(page_records["gradient"])

        page = HeatFlowPage(page_records["child"], member)

        assert page.opens(page_records["gradient"]) is True

    def test_nothing_opens_for_a_record_that_is_not_there(self, page_records, visitor):
        page = HeatFlowPage(page_records["child"], visitor)

        assert page.opens(None) is False


class TestHeatFlowPageSplit:
    def test_it_returns_the_records_the_visitor_may_open_and_counts_the_rest(
        self, page_records, hide, visitor
    ):
        hide(page_records["conductivity"])
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
        self, page_records, hide, visitor
    ):
        hide(page_records["interval"])

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

    def test_it_returns_the_elevation_and_uncertainty_of_the_sites_location(
        self, page_records, visitor
    ):
        HeatFlowSite.objects.filter(pk=page_records["site"].pk).update(
            location_elevation=125, location_uncertainty=40
        )
        interval = HeatFlowInterval.objects.get(pk=page_records["interval"].pk)

        place = HeatFlowPage(interval, visitor).site_location()

        assert place["elevation"] == interval.site.location_elevation
        assert place["uncertainty"] == interval.site.location_uncertainty
        assert place["elevation"] is not None
        assert place["uncertainty"] is not None

    def test_a_site_the_visitor_may_not_open_gives_no_location(
        self, page_records, hide, visitor
    ):
        hide(page_records["site"])

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
        self, page_records, hide, visitor, name
    ):
        hide(page_records[name])

        context = HeatFlowPage(page_records["child"], visitor).for_child()

        assert context[name] is None
        assert context[f"{name}_hidden"] is True

    def test_the_interval_and_site_in_an_unpublished_dataset_are_not_returned(
        self, page_records, hide, visitor
    ):
        hide(page_records["interval"])
        hide(page_records["site"])

        context = HeatFlowPage(page_records["child"], visitor).for_child()

        assert context["interval"] is None
        assert context["site"] is None
        assert context["location"]["visible"] is False

    def test_a_member_is_given_the_unpublished_records(
        self, page_records, hide, member
    ):
        hide(page_records["gradient"])

        context = HeatFlowPage(page_records["child"], member).for_child()

        assert context["gradient"] == page_records["gradient"]
        assert context["gradient_hidden"] is False

    def test_it_says_whether_the_childs_scores_are_stale(self, page_records, visitor):
        child = page_records["child"]
        HeatFlow.objects.filter(pk=child.pk).update(quality_scheme="hfqa_tool 0.1")
        child.refresh_from_db()

        assert HeatFlowPage(child, visitor).for_child()["stale"] is True


class TestHeatFlowPageForInterval:
    def test_it_returns_the_site_the_visitor_may_open(self, page_records, visitor):
        context = HeatFlowPage(page_records["interval"], visitor).for_interval()

        assert context["site"] == page_records["site"]
        assert context["site_hidden"] is False

    def test_a_site_in_an_unpublished_dataset_is_marked_hidden_and_not_returned(
        self, page_records, hide, visitor
    ):
        hide(page_records["site"])

        context = HeatFlowPage(page_records["interval"], visitor).for_interval()

        assert context["site"] is None
        assert context["site_hidden"] is True

    def test_a_member_is_given_the_unpublished_site(self, page_records, hide, member):
        hide(page_records["site"])

        context = HeatFlowPage(page_records["interval"], member).for_interval()

        assert context["site"] == page_records["site"]
        assert context["site_hidden"] is False

    def test_it_returns_the_probe_metadata_recorded_for_the_interval(
        self, page_records, visitor
    ):
        probe = ProbeMetadataFactory(interval=page_records["interval"])
        interval = HeatFlowInterval.objects.get(pk=page_records["interval"].pk)

        context = HeatFlowPage(interval, visitor).for_interval()

        assert context["probe"] == probe

    def test_an_interval_without_probe_metadata_gets_none(self, page_records, visitor):
        context = HeatFlowPage(page_records["interval"], visitor).for_interval()

        assert context["probe"] is None

    def test_it_returns_the_location_of_the_intervals_site(self, page_records, visitor):
        page = HeatFlowPage(page_records["interval"], visitor)

        assert page.for_interval()["location"] == page.site_location()

    def test_it_returns_the_igsn_recorded_for_the_interval(self, page_records, visitor):
        SampleIdentifier.objects.create(
            related=page_records["interval"], type="IGSN", value="10.60510/IEGHF0001"
        )

        context = HeatFlowPage(page_records["interval"], visitor).for_interval()

        assert context["igsn"] == "10.60510/IEGHF0001"

    def test_an_interval_without_an_igsn_gets_an_empty_one(self, page_records, visitor):
        SampleIdentifier.objects.create(
            related=page_records["interval"], type="DOI", value="10.1234/other"
        )

        context = HeatFlowPage(page_records["interval"], visitor).for_interval()

        assert context["igsn"] == ""

    def test_it_makes_one_query_each_for_the_site_the_probe_and_the_igsn(
        self, page_records, visitor
    ):
        interval = HeatFlowInterval.objects.select_related("site").get(
            pk=page_records["interval"].pk
        )
        page = HeatFlowPage(interval, visitor)

        assert query_count(page.for_interval) == 3


def add_interval(site, top, bottom, dataset, children=0):
    """Add an interval to ``site`` with ``children`` heat flow values over it."""
    interval = HeatFlowIntervalFactory(
        dataset=dataset, site=site, top=top, bottom=bottom
    )
    kids = [HeatFlowFactory(dataset=dataset, sample=interval) for _ in range(children)]
    return interval, kids


def query_count(action):
    """Count the queries ``action`` makes."""
    with CaptureQueriesContext(connection) as queries:
        action()
    return len(queries)


class TestHeatFlowPageForSite:
    def test_it_returns_the_parent_the_visitor_may_open(self, page_records, visitor):
        context = HeatFlowPage(page_records["site"], visitor).for_site()

        assert context["parent"] == page_records["parent"]
        assert context["parent_hidden"] is False

    def test_a_site_without_a_parent_gets_none_and_no_hidden_mark(
        self, page_records, visitor
    ):
        ParentHeatFlow.objects.filter(pk=page_records["parent"].pk).delete()

        context = HeatFlowPage(page_records["site"], visitor).for_site()

        assert context["parent"] is None
        assert context["parent_hidden"] is False

    def test_a_parent_in_an_unpublished_dataset_is_marked_hidden_and_not_returned(
        self, page_records, hide, visitor
    ):
        hide(page_records["parent"])

        context = HeatFlowPage(page_records["site"], visitor).for_site()

        assert context["parent"] is None
        assert context["parent_hidden"] is True

    def test_a_member_is_given_the_unpublished_parent(self, page_records, hide, member):
        hide(page_records["parent"])

        context = HeatFlowPage(page_records["site"], member).for_site()

        assert context["parent"] == page_records["parent"]
        assert context["parent_hidden"] is False

    def test_intervals_run_from_shallowest_to_deepest_ties_broken_by_bottom_then_pk(
        self, page_records, published_dataset, visitor
    ):
        site = page_records["site"]
        deep, _ = add_interval(site, 300, 400, published_dataset)
        wide, _ = add_interval(site, 100, 900, published_dataset)
        first, _ = add_interval(site, 100, 200, published_dataset)
        second, _ = add_interval(site, 100, 200, published_dataset)

        rows = HeatFlowPage(site, visitor).for_site()["intervals"]["rows"]

        assert [row["interval"] for row in rows] == [
            page_records["interval"],
            first,
            second,
            wide,
            deep,
        ]

    def test_each_interval_carries_the_children_determined_over_it(
        self, page_records, published_dataset, visitor
    ):
        site = page_records["site"]
        other, kids = add_interval(site, 600, 700, published_dataset, children=2)

        rows = HeatFlowPage(site, visitor).for_site()["intervals"]["rows"]

        by_interval = {row["interval"]: row["children"] for row in rows}
        assert set(by_interval[other]["rows"]) == set(kids)
        assert by_interval[page_records["interval"]]["rows"] == [page_records["child"]]
        assert by_interval[other]["hidden"] == 0

    def test_an_interval_in_an_unpublished_dataset_is_counted_and_not_returned(
        self, page_records, published_dataset, hide, visitor
    ):
        site = page_records["site"]
        add_interval(site, 600, 700, published_dataset)
        concealed, _ = add_interval(site, 800, 900, published_dataset)
        hide(concealed)

        intervals = HeatFlowPage(site, visitor).for_site()["intervals"]

        assert concealed not in [row["interval"] for row in intervals["rows"]]
        assert intervals["hidden"] == 1
        assert intervals["total"] == 2

    def test_a_child_in_an_unpublished_dataset_is_counted_against_its_interval(
        self, page_records, hide, visitor
    ):
        concealed = HeatFlowFactory(
            dataset=page_records["child"].dataset, sample=page_records["interval"]
        )
        hide(concealed)

        rows = HeatFlowPage(page_records["site"], visitor).for_site()["intervals"][
            "rows"
        ]

        children = rows[0]["children"]
        assert children["rows"] == [page_records["child"]]
        assert children["hidden"] == 1

    def test_a_member_is_given_the_unpublished_child(self, page_records, hide, member):
        concealed = HeatFlowFactory(
            dataset=page_records["child"].dataset, sample=page_records["interval"]
        )
        hide(concealed)

        rows = HeatFlowPage(page_records["site"], member).for_site()["intervals"][
            "rows"
        ]

        assert concealed in rows[0]["children"]["rows"]
        assert rows[0]["children"]["hidden"] == 0

    def test_it_cuts_the_intervals_at_the_limit_and_counts_the_rest(
        self, page_records, published_dataset, visitor
    ):
        site = page_records["site"]
        for top in (100, 200, 300):
            add_interval(site, top, top + 50, published_dataset)
        page = HeatFlowPage(site, visitor)
        page.intervals_shown = 2

        intervals = page.for_site()["intervals"]

        assert len(intervals["rows"]) == 2
        assert intervals["more"] == 2
        assert intervals["total"] == 4

    def test_show_all_lifts_the_cut(self, page_records, published_dataset, visitor):
        site = page_records["site"]
        for top in (100, 200, 300):
            add_interval(site, top, top + 50, published_dataset)
        page = HeatFlowPage(site, visitor, show_all=True)
        page.intervals_shown = 2

        intervals = page.for_site()["intervals"]

        assert len(intervals["rows"]) == 4
        assert intervals["more"] == 0

    def test_it_counts_the_children_over_every_interval_the_visitor_may_open(
        self, page_records, published_dataset, visitor
    ):
        site = page_records["site"]
        add_interval(site, 100, 200, published_dataset, children=2)
        add_interval(site, 300, 400, published_dataset, children=1)
        page = HeatFlowPage(site, visitor)
        page.intervals_shown = 1

        assert page.for_site()["intervals"]["children"] == 4

    def test_it_prefetches_what_the_page_reads_from_each_interval_and_child(
        self, page_records, published_dataset, visitor, django_assert_num_queries
    ):
        site = page_records["site"]
        add_interval(site, 100, 200, published_dataset, children=2)

        rows = HeatFlowPage(site, visitor).for_site()["intervals"]["rows"]

        with django_assert_num_queries(0):
            for row in rows:
                list(row["interval"].lithology.all())
                for child in row["children"]["rows"]:
                    list(child.method.all())

    def test_it_makes_the_same_queries_for_one_interval_and_for_three(
        self, page_records, published_dataset, visitor
    ):
        site = page_records["site"]

        def gather():
            return HeatFlowPage(site, visitor).for_site()

        with_one = query_count(gather)
        for top in (100, 200):
            add_interval(site, top, top + 50, published_dataset, children=2)

        with_three = query_count(gather)

        assert with_three == with_one


def add_users(page_records, dataset, count):
    """Add ``count`` children using the records' gradient and conductivity."""
    return [
        HeatFlowFactory(
            dataset=dataset,
            sample=page_records["interval"],
            thermal_gradient=page_records["gradient"],
            thermal_conductivity=page_records["conductivity"],
        )
        for _ in range(count)
    ]


class TestHeatFlowPageForGradientOrConductivity:
    @pytest.fixture(params=["gradient", "conductivity"])
    def measurement(self, request, page_records):
        return page_records[request.param]

    def test_it_returns_the_interval_and_the_site_the_visitor_may_open(
        self, page_records, measurement, visitor
    ):
        page = HeatFlowPage(measurement, visitor)

        context = page.for_gradient_or_conductivity()

        assert context["interval"] == page_records["interval"]
        assert context["site"] == page_records["site"]
        assert context["location"]["visible"] is True

    def test_the_interval_and_site_in_an_unpublished_dataset_are_not_returned(
        self, page_records, measurement, hide, visitor
    ):
        hide(page_records["interval"])
        hide(page_records["site"])

        page = HeatFlowPage(measurement, visitor)
        context = page.for_gradient_or_conductivity()

        assert context["interval"] is None
        assert context["site"] is None
        assert context["location"]["visible"] is False

    def test_it_returns_the_children_that_use_the_measurement(
        self, page_records, published_dataset, measurement, visitor
    ):
        (other,) = add_users(page_records, published_dataset, 1)
        unrelated = HeatFlowFactory(
            dataset=published_dataset, sample=page_records["interval"]
        )

        page = HeatFlowPage(measurement, visitor)
        children = page.for_gradient_or_conductivity()["children"]

        assert set(children["rows"]) == {page_records["child"], other}
        assert unrelated not in children["rows"]
        assert children["total"] == 2
        assert children["hidden"] == 0

    def test_a_child_in_an_unpublished_dataset_is_counted_and_not_returned(
        self, page_records, published_dataset, measurement, hide, visitor
    ):
        (concealed,) = add_users(page_records, published_dataset, 1)
        hide(concealed)

        page = HeatFlowPage(measurement, visitor)
        children = page.for_gradient_or_conductivity()["children"]

        assert children["rows"] == [page_records["child"]]
        assert children["hidden"] == 1

    def test_a_member_is_given_the_unpublished_child(
        self, page_records, published_dataset, measurement, hide, member
    ):
        (concealed,) = add_users(page_records, published_dataset, 1)
        hide(concealed)

        page = HeatFlowPage(measurement, member)
        children = page.for_gradient_or_conductivity()["children"]

        assert concealed in children["rows"]
        assert children["hidden"] == 0

    def test_it_cuts_the_children_at_the_limit_and_counts_the_rest(
        self, page_records, published_dataset, measurement, visitor
    ):
        add_users(page_records, published_dataset, 2)
        page = HeatFlowPage(measurement, visitor)
        page.children_shown = 2

        children = page.for_gradient_or_conductivity()["children"]

        assert len(children["rows"]) == 2
        assert children["more"] == 1
        assert children["total"] == 3

    def test_show_all_lifts_the_cut(
        self, page_records, published_dataset, measurement, visitor
    ):
        add_users(page_records, published_dataset, 2)
        page = HeatFlowPage(measurement, visitor, show_all=True)
        page.children_shown = 2

        children = page.for_gradient_or_conductivity()["children"]

        assert len(children["rows"]) == 3
        assert children["more"] == 0

    def test_it_prefetches_the_method_of_each_listed_child(
        self,
        page_records,
        published_dataset,
        measurement,
        visitor,
        django_assert_num_queries,
    ):
        add_users(page_records, published_dataset, 2)

        page = HeatFlowPage(measurement, visitor)
        children = page.for_gradient_or_conductivity()["children"]

        with django_assert_num_queries(0):
            for child in children["rows"]:
                list(child.method.all())

    def test_it_makes_the_same_queries_for_one_child_and_for_three(
        self, page_records, published_dataset, measurement, visitor
    ):
        def gather():
            return HeatFlowPage(measurement, visitor).for_gradient_or_conductivity()

        with_one = query_count(gather)
        add_users(page_records, published_dataset, 2)

        assert query_count(gather) == with_one

    def test_it_says_whether_the_measurements_score_is_stale(
        self, measurement, visitor
    ):
        type(measurement).objects.filter(pk=measurement.pk).update(
            quality_scheme="hfqa_tool 0.1"
        )
        measurement.refresh_from_db()

        page = HeatFlowPage(measurement, visitor)

        assert page.for_gradient_or_conductivity()["stale"] is True


def add_children(page_records, dataset, count, is_relevant=False):
    """Add ``count`` children to the page's parent."""
    return [
        HeatFlowFactory(
            dataset=dataset,
            sample=page_records["interval"],
            parent=page_records["parent"],
            is_relevant=is_relevant,
        )
        for _ in range(count)
    ]


class TestHeatFlowPageForParent:
    def test_it_returns_every_child_with_its_relevance(
        self, page_records, published_dataset, visitor
    ):
        relevant = add_children(page_records, published_dataset, 2, is_relevant=True)
        (other,) = add_children(page_records, published_dataset, 1)
        unrelated = HeatFlowFactory(
            dataset=published_dataset, sample=page_records["interval"]
        )

        page = HeatFlowPage(page_records["parent"], visitor)
        children = page.for_parent()["children"]

        assert set(children["rows"]) == {page_records["child"], other, *relevant}
        assert unrelated not in children["rows"]
        assert {row.pk: row.is_relevant for row in children["rows"]} == {
            page_records["child"].pk: False,
            other.pk: False,
            relevant[0].pk: True,
            relevant[1].pk: True,
        }
        assert children["total"] == 4
        assert children["hidden"] == 0

    def test_an_only_child_is_what_the_quality_rests_on(self, page_records, visitor):
        context = HeatFlowPage(page_records["parent"], visitor).for_parent()

        assert context["basis"] == "single"
        assert context["rests_on"] == {page_records["child"].pk}

    def test_several_children_rest_the_quality_on_the_relevant_ones(
        self, page_records, published_dataset, visitor
    ):
        relevant = add_children(page_records, published_dataset, 2, is_relevant=True)

        context = HeatFlowPage(page_records["parent"], visitor).for_parent()

        assert context["basis"] == "relevant"
        assert context["rests_on"] == {child.pk for child in relevant}

    def test_each_child_says_whether_the_quality_rests_on_it(
        self, page_records, published_dataset, visitor
    ):
        add_children(page_records, published_dataset, 2, is_relevant=True)

        context = HeatFlowPage(page_records["parent"], visitor).for_parent()

        for child in context["children"]["rows"]:
            assert child.rests_on is (child.pk in context["rests_on"])

    def test_several_children_and_none_relevant_rest_the_quality_on_nothing(
        self, page_records, published_dataset, visitor
    ):
        add_children(page_records, published_dataset, 1)

        context = HeatFlowPage(page_records["parent"], visitor).for_parent()

        assert context["basis"] == "none"
        assert context["rests_on"] == set()
        assert context["children"]["total"] == 2

    def test_a_parent_with_no_children_has_an_empty_basis(self, page_records, visitor):
        page_records["child"].delete()

        context = HeatFlowPage(page_records["parent"], visitor).for_parent()

        assert context["basis"] == "empty"
        assert context["rests_on"] == set()
        assert context["children"]["rows"] == []

    def test_a_child_in_an_unpublished_dataset_is_counted_and_not_returned(
        self, page_records, published_dataset, hide, visitor
    ):
        (concealed,) = add_children(page_records, published_dataset, 1)
        hide(concealed)

        children = HeatFlowPage(page_records["parent"], visitor).for_parent()[
            "children"
        ]

        assert children["rows"] == [page_records["child"]]
        assert children["hidden"] == 1

    def test_a_member_is_given_the_unpublished_child(
        self, page_records, published_dataset, hide, member
    ):
        (concealed,) = add_children(page_records, published_dataset, 1)
        hide(concealed)

        children = HeatFlowPage(page_records["parent"], member).for_parent()["children"]

        assert concealed in children["rows"]
        assert children["hidden"] == 0

    def test_a_hidden_child_still_counts_towards_what_the_quality_rests_on(
        self, page_records, published_dataset, hide, visitor
    ):
        (concealed,) = add_children(page_records, published_dataset, 1, True)
        hide(concealed)

        context = HeatFlowPage(page_records["parent"], visitor).for_parent()

        assert context["basis"] == "relevant"
        assert context["rests_on"] == {concealed.pk}

    def test_it_cuts_the_children_at_the_limit_and_counts_the_rest(
        self, page_records, published_dataset, visitor
    ):
        add_children(page_records, published_dataset, 2)
        page = HeatFlowPage(page_records["parent"], visitor)
        page.children_shown = 2

        children = page.for_parent()["children"]

        assert len(children["rows"]) == 2
        assert children["more"] == 1
        assert children["total"] == 3

    def test_show_all_lifts_the_cut(self, page_records, published_dataset, visitor):
        add_children(page_records, published_dataset, 2)
        page = HeatFlowPage(page_records["parent"], visitor, show_all=True)
        page.children_shown = 2

        children = page.for_parent()["children"]

        assert len(children["rows"]) == 3
        assert children["more"] == 0

    def test_it_returns_the_site_the_visitor_may_open(self, page_records, visitor):
        context = HeatFlowPage(page_records["parent"], visitor).for_parent()

        assert context["site"] == page_records["site"]
        assert context["location"]["visible"] is True

    def test_a_site_in_an_unpublished_dataset_is_not_returned(
        self, page_records, hide, visitor
    ):
        hide(page_records["site"])

        context = HeatFlowPage(page_records["parent"], visitor).for_parent()

        assert context["site"] is None
        assert context["location"]["visible"] is False

    def test_it_prefetches_the_method_of_each_listed_child(
        self, page_records, published_dataset, visitor, django_assert_num_queries
    ):
        add_children(page_records, published_dataset, 2)

        children = HeatFlowPage(page_records["parent"], visitor).for_parent()[
            "children"
        ]

        with django_assert_num_queries(0):
            for child in children["rows"]:
                list(child.method.all())

    def test_it_makes_the_same_queries_for_one_child_and_for_three(
        self, page_records, published_dataset, visitor
    ):
        def gather():
            return HeatFlowPage(page_records["parent"], visitor).for_parent()

        with_one = query_count(gather)
        add_children(page_records, published_dataset, 2)

        assert query_count(gather) == with_one

    def test_it_says_whether_the_parents_score_is_stale(self, page_records, visitor):
        parent = page_records["parent"]
        ParentHeatFlow.objects.filter(pk=parent.pk).update(
            quality_scheme="hfqa_tool 0.1"
        )
        parent.refresh_from_db()

        assert HeatFlowPage(parent, visitor).for_parent()["stale"] is True
