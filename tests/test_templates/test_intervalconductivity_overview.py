# Tests for the interval conductivity's overview page, read through its URL. The page's
# content is found by the ``data-`` hooks its templates carry, never by wording. Mirrors
# no Python module: the subject is the templates under ``project/heat_flow/templates/``
# and ``templates/cotton/``, declared under ``non-mirror-paths`` in pyproject.toml.

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from fairdm.contrib.contributors.choices import ContributionLevel
from fairdm.factories import ContributionFactory, PersonFactory
from heat_flow import vocabularies
from heat_flow.models import IntervalConductivity
from heat_flow.overview import HeatFlowPage

from tests.factories import HeatFlowFactory

pytestmark = pytest.mark.django_db

SHOW_ALL = "?show=all#children"
CONCEPT_FIELDS = (
    "source",
    "conductivity_location",
    "method",
    "strategy",
    "saturation",
    "pT_conditions",
    "pT_function",
)


def link_to(node, record):
    """Say whether ``node`` links to ``record``'s page."""
    return record.get_absolute_url() in node.hrefs


def a_term_of(record, field_name):
    """One concept of the vocabulary ``record``'s field declares."""
    vocabulary = type(record)._meta.get_field(field_name).vocabulary[0]
    return vocabularies.concepts(vocabulary).first()


def shows_term(node, concept):
    """Say whether ``node`` shows a vocabulary concept's label, in any case.

    The page may capitalise the first letter.
    """
    return concept.display_label().casefold() in node.text.casefold()


def shown(score):
    """A stored score as the page writes it in ``data-value``."""
    return f"{score:.1f}"


def add_users(page_records, dataset, count):
    """Add ``count`` children that use the page's conductivity."""
    return [
        HeatFlowFactory(
            dataset=dataset,
            sample=page_records["interval"],
            thermal_conductivity=page_records["conductivity"],
        )
        for _ in range(count)
    ]


def listed(page):
    """The children the page lists, by primary key."""
    rows = page.find("data-heat-flow", "children").find_all("data-child")
    return [int(row.attrs["data-child"]) for row in rows]


@pytest.fixture
def small_cut(monkeypatch):
    """Cut a list of children at two."""
    monkeypatch.setattr(HeatFlowPage, "children_shown", 2)


class TestConductivityPage:
    def test_it_shows_the_value_with_its_uncertainty_and_unit(
        self, document, page_records
    ):
        conductivity = page_records["conductivity"]

        page = document(conductivity)

        assert conductivity.print_value() in page.find("data-field", "value").text

    def test_it_shows_each_vocabulary_backed_field_as_its_terms(
        self, document, page_records
    ):
        conductivity = page_records["conductivity"]
        for name in CONCEPT_FIELDS:
            manager = getattr(conductivity, name)
            manager.set([a_term_of(conductivity, name)])

        page = document(conductivity)

        for name in CONCEPT_FIELDS:
            concept = getattr(conductivity, name).first()
            node = page.find("data-field", name)
            assert shows_term(node, concept)
            assert "data-state" not in node.attrs

    def test_it_shows_the_number_of_measurements(self, document, page_records):
        conductivity = page_records["conductivity"]

        page = document(conductivity)

        assert str(conductivity.number) in page.find("data-field", "number").text

    def test_a_field_with_nothing_recorded_says_it_is_not_recorded(
        self, document, page_records
    ):
        conductivity = page_records["conductivity"]
        conductivity.strategy.set([])
        IntervalConductivity.objects.filter(pk=conductivity.pk).update(number=None)

        page = document(conductivity)

        for name in ("strategy", "number"):
            assert page.find("data-field", name).attrs["data-state"] == "not-recorded"

    def test_it_links_the_depth_interval_and_the_site_it_was_measured_over(
        self, document, page_records
    ):
        page = document(page_records["conductivity"])

        assert link_to(
            page.find("data-heat-flow", "interval"), page_records["interval"]
        )
        assert link_to(page.find("data-heat-flow", "site"), page_records["site"])

    def test_it_lists_the_children_that_use_it_each_linked(
        self, document, page_records, published_dataset
    ):
        others = add_users(page_records, published_dataset, 2)
        unrelated = HeatFlowFactory(
            dataset=published_dataset, sample=page_records["interval"]
        )

        page = document(page_records["conductivity"])

        children = page.find("data-heat-flow", "children")
        assert set(listed(page)) == {page_records["child"].pk, *(o.pk for o in others)}
        for child in (page_records["child"], *others):
            assert link_to(children, child)
        assert not link_to(children, unrelated)

    def test_a_conductivity_no_child_uses_says_so(self, document, page_records):
        page_records["child"].delete()

        page = document(page_records["conductivity"])

        assert page.find("data-heat-flow", "children").attrs["data-state"] == "empty"

    def test_a_stale_scheme_revision_is_said_to_be_stale(self, document, page_records):
        conductivity = page_records["conductivity"]
        IntervalConductivity.objects.filter(pk=conductivity.pk).update(
            quality_scheme="hfqa_tool 0.1"
        )
        conductivity.refresh_from_db()

        assert document(conductivity).find("data-state", "stale") is not None

    def test_the_current_scheme_revision_is_not_said_to_be_stale(
        self, document, page_records
    ):
        conductivity = page_records["conductivity"]
        IntervalConductivity.objects.filter(pk=conductivity.pk).update(
            quality_scheme="hfqa_tool 0.2"
        )
        conductivity.refresh_from_db()

        assert document(conductivity).find("data-state", "stale") is None


class TestConductivityPageCutList:
    def test_it_shows_the_cut_and_says_how_many_more(
        self, document, page_records, published_dataset, small_cut
    ):
        add_users(page_records, published_dataset, 2)

        page = document(page_records["conductivity"])

        assert len(listed(page)) == 2
        assert page.find("data-heat-flow", "children").attrs["data-more"] == "1"

    def test_it_links_to_the_same_page_asking_for_all_of_them(
        self, document, page_records, published_dataset, small_cut
    ):
        add_users(page_records, published_dataset, 2)

        page = document(page_records["conductivity"])

        assert SHOW_ALL in page.find("data-heat-flow", "children").hrefs

    def test_show_all_lists_every_child_and_drops_the_link(
        self, document, page_records, published_dataset, small_cut
    ):
        add_users(page_records, published_dataset, 2)

        page = document(page_records["conductivity"], show="all")

        children = page.find("data-heat-flow", "children")
        assert len(listed(page)) == 3
        assert "data-more" not in children.attrs
        assert SHOW_ALL not in children.hrefs

    def test_a_conductivity_within_the_cut_has_no_remainder(
        self, document, page_records
    ):
        page = document(page_records["conductivity"])

        children = page.find("data-heat-flow", "children")
        assert "data-more" not in children.attrs
        assert SHOW_ALL not in children.hrefs


class TestConductivityPageForARecordTheVisitorMayNotOpen:
    def test_a_hidden_child_is_counted_and_never_linked(
        self, document, page_records, published_dataset, hide
    ):
        (concealed,) = add_users(page_records, published_dataset, 1)
        hide(concealed)

        page = document(page_records["conductivity"])

        children = page.find("data-heat-flow", "children")
        assert children.attrs["data-hidden"] == "1"
        assert link_to(children, page_records["child"])
        assert concealed.get_absolute_url() not in page.root.hrefs

    def test_a_conductivity_whose_children_are_all_hidden_is_not_said_to_be_unused(
        self, document, page_records, hide
    ):
        hide(page_records["child"])

        page = document(page_records["conductivity"])

        children = page.find("data-heat-flow", "children")
        assert children.attrs["data-hidden"] == "1"
        assert "data-state" not in children.attrs

    def test_a_hidden_interval_and_site_are_not_linked(
        self, document, page_records, hide
    ):
        hide(page_records["interval"])
        hide(page_records["site"])

        page = document(page_records["conductivity"])

        for name in ("interval", "site"):
            assert page.find("data-heat-flow", name).attrs["data-state"] == "hidden"
        assert page_records["interval"].get_absolute_url() not in page.root.hrefs
        assert page_records["site"].get_absolute_url() not in page.root.hrefs

    def test_a_member_of_the_dataset_is_shown_the_hidden_child(
        self, document, page_records, published_dataset, hide, member
    ):
        (concealed,) = add_users(page_records, published_dataset, 1)
        hide(concealed)

        page = document(page_records["conductivity"], user=member)

        children = page.find("data-heat-flow", "children")
        assert link_to(children, concealed)
        assert "data-hidden" not in children.attrs


class TestConductivityPageKeepsFairDMsPage:
    def test_it_keeps_the_identifiers_and_citation_cards(self, document, page_records):
        page = document(page_records["conductivity"])

        assert page.find("data-card", "identifiers") is not None
        assert page.find("data-card", "citation") is not None

    def test_a_dataset_manager_is_shown_the_manage_menu(self, document, page_records):
        manager = PersonFactory(is_claimed=True, password="test-pass-123")
        ContributionFactory(
            contributor=manager,
            content_object=page_records["conductivity"].dataset,
            level=ContributionLevel.MANAGE,
        )

        page = document(page_records["conductivity"], user=manager)

        assert page.find("data-menu", "manage") is not None

    def test_a_visitor_is_not_shown_the_manage_menu(self, document, page_records):
        assert (
            document(page_records["conductivity"]).find("data-menu", "manage") is None
        )


class TestConductivityPageQueries:
    def test_the_page_makes_the_same_queries_for_one_child_and_for_three(
        self, client, page_records, published_dataset
    ):
        url = page_records["conductivity"].get_absolute_url()

        def count():
            with CaptureQueriesContext(connection) as queries:
                assert client.get(url).status_code == 200
            return len(queries)

        count()
        with_one = count()
        add_users(page_records, published_dataset, 2)

        with_three = count()

        assert with_three == with_one


class TestMeasurementCard:
    """The conductivity's own quality card, moved from FS-007's page tests."""

    def test_a_conductivity_shows_its_own_score_and_its_mark(self, page, conductivity):
        card = page(conductivity)

        assert card.cards == ["conductivity"]
        assert card.hooks["own"].value == shown(conductivity.score)
        assert card.hooks["own"].missing == "true"
        assert card.hooks["own"].marks
