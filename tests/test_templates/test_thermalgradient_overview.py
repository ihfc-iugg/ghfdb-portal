# Tests for the thermal gradient's overview page, read through its URL. The page's
# content is found by the ``data-`` hooks its templates carry, never by wording. Mirrors
# no Python module: the subject is the templates under ``project/heat_flow/templates/``
# and ``templates/cotton/``, declared under ``non-mirror-paths`` in pyproject.toml.

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from fairdm.contrib.contributors.choices import ContributionLevel
from fairdm.factories import ContributionFactory, PersonFactory
from heat_flow.models import ThermalGradient
from heat_flow.overview import HeatFlowPage

from tests.factories import (
    HeatFlowFactory,
    HeatFlowIntervalFactory,
    HeatFlowSiteFactory,
    ParentHeatFlowFactory,
    ThermalGradientFactory,
)

pytestmark = pytest.mark.django_db

SHOW_ALL = "?show=all#children"
TEMPERATURE_FIELDS = (
    "temperature_top",
    "temperature_bottom",
    "method_top",
    "method_bottom",
    "correction_top",
    "correction_bottom",
    "shutin_top",
    "shutin_bottom",
    "number",
)


def link_to(node, record):
    """Say whether ``node`` links to ``record``'s page."""
    return record.get_absolute_url() in node.hrefs


def shows_term(node, concept):
    """Say whether ``node`` shows a vocabulary concept's English label, in any case.

    A graph concept gives its label as a method; the page capitalises the first letter.
    """
    label = concept.label
    label = str(label("en") if callable(label) else label)
    return label.casefold() in node.text.casefold()


def shown(score):
    """A stored score as the page writes it in ``data-value``."""
    return f"{score:.1f}"


def add_users(page_records, dataset, count):
    """Add ``count`` children that use the page's gradient."""
    return [
        HeatFlowFactory(
            dataset=dataset,
            sample=page_records["interval"],
            thermal_gradient=page_records["gradient"],
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


class TestGradientPage:
    def test_it_shows_the_measured_and_corrected_gradient_with_uncertainties_and_units(
        self, document, page_records
    ):
        gradient = page_records["gradient"]
        gradient.refresh_from_db()
        corrected = gradient.corrected_value
        uncertainty = gradient.corrected_uncertainty

        page = document(gradient)

        assert gradient.print_value() in page.find("data-field", "value").text
        text = page.find("data-field", "corrected_value").text
        assert (
            f"{corrected.magnitude} ± {uncertainty.magnitude} {corrected.units:~P}"
            in (text)
        )

    def test_a_gradient_without_a_corrected_value_says_it_is_not_recorded(
        self, document, page_records
    ):
        gradient = page_records["gradient"]
        ThermalGradient.objects.filter(pk=gradient.pk).update(
            corrected_value=None, corrected_uncertainty=None
        )
        gradient.refresh_from_db()

        page = document(gradient)

        field = page.find("data-field", "corrected_value")
        assert field.attrs["data-state"] == "not-recorded"

    def test_it_shows_the_temperatures_methods_corrections_shut_in_times_and_number(
        self, document, page_records
    ):
        gradient = page_records["gradient"]
        top, bottom = gradient.method_top.first(), gradient.method_bottom.first()
        gradient.correction_top.set(gradient.correction_top.model.objects.all()[:1])
        gradient.correction_bottom.set(
            gradient.correction_bottom.model.objects.all()[:1]
        )
        ThermalGradient.objects.filter(pk=gradient.pk).update(
            temperature_top=20, temperature_bottom=45
        )
        gradient.refresh_from_db()

        page = document(gradient)

        for name in TEMPERATURE_FIELDS:
            assert page.find("data-field", name) is not None
        assert shows_term(page.find("data-field", "method_top"), top)
        assert shows_term(page.find("data-field", "method_bottom"), bottom)
        assert shows_term(
            page.find("data-field", "correction_top"), gradient.correction_top.first()
        )
        assert str(gradient.number) in page.find("data-field", "number").text
        assert str(gradient.shutin_top.magnitude) in (
            page.find("data-field", "shutin_top").text
        )
        assert "data-state" not in page.find("data-field", "temperature_top").attrs

    def test_a_field_with_nothing_recorded_says_it_is_not_recorded(
        self, document, page_records
    ):
        gradient = page_records["gradient"]
        ThermalGradient.objects.filter(pk=gradient.pk).update(
            shutin_top=None, number=None
        )
        gradient.refresh_from_db()

        page = document(gradient)

        for name in ("shutin_top", "number"):
            assert page.find("data-field", name).attrs["data-state"] == "not-recorded"
        assert "data-state" not in page.find("data-field", "shutin_bottom").attrs

    def test_it_links_the_depth_interval_and_the_site_it_was_measured_over(
        self, document, page_records
    ):
        page = document(page_records["gradient"])

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

        page = document(page_records["gradient"])

        children = page.find("data-heat-flow", "children")
        assert set(listed(page)) == {page_records["child"].pk, *(o.pk for o in others)}
        for child in (page_records["child"], *others):
            assert link_to(children, child)
        assert not link_to(children, unrelated)

    def test_a_gradient_no_child_uses_says_so(self, document, page_records):
        page_records["child"].delete()

        page = document(page_records["gradient"])

        assert page.find("data-heat-flow", "children").attrs["data-state"] == "empty"

    def test_a_stale_scheme_revision_is_said_to_be_stale(self, document, page_records):
        gradient = page_records["gradient"]
        ThermalGradient.objects.filter(pk=gradient.pk).update(
            quality_scheme="hfqa_tool 0.1"
        )
        gradient.refresh_from_db()

        assert document(gradient).find("data-state", "stale") is not None

    def test_the_current_scheme_revision_is_not_said_to_be_stale(
        self, document, page_records
    ):
        gradient = page_records["gradient"]
        ThermalGradient.objects.filter(pk=gradient.pk).update(
            quality_scheme="hfqa_tool 0.2"
        )
        gradient.refresh_from_db()

        assert document(gradient).find("data-state", "stale") is None


class TestGradientPageCutList:
    def test_it_shows_the_cut_and_says_how_many_more(
        self, document, page_records, published_dataset, small_cut
    ):
        add_users(page_records, published_dataset, 2)

        page = document(page_records["gradient"])

        assert len(listed(page)) == 2
        assert page.find("data-heat-flow", "children").attrs["data-more"] == "1"

    def test_it_links_to_the_same_page_asking_for_all_of_them(
        self, document, page_records, published_dataset, small_cut
    ):
        add_users(page_records, published_dataset, 2)

        page = document(page_records["gradient"])

        assert SHOW_ALL in page.find("data-heat-flow", "children").hrefs

    def test_show_all_lists_every_child_and_drops_the_link(
        self, document, page_records, published_dataset, small_cut
    ):
        add_users(page_records, published_dataset, 2)

        page = document(page_records["gradient"], show="all")

        children = page.find("data-heat-flow", "children")
        assert len(listed(page)) == 3
        assert "data-more" not in children.attrs
        assert SHOW_ALL not in children.hrefs

    def test_a_gradient_within_the_cut_has_no_remainder(self, document, page_records):
        page = document(page_records["gradient"])

        children = page.find("data-heat-flow", "children")
        assert "data-more" not in children.attrs
        assert SHOW_ALL not in children.hrefs


class TestGradientPageForARecordTheVisitorMayNotOpen:
    def test_a_hidden_child_is_counted_and_never_linked(
        self, document, page_records, published_dataset, hide
    ):
        (concealed,) = add_users(page_records, published_dataset, 1)
        hide(concealed)

        page = document(page_records["gradient"])

        children = page.find("data-heat-flow", "children")
        assert children.attrs["data-hidden"] == "1"
        assert link_to(children, page_records["child"])
        assert concealed.get_absolute_url() not in page.root.hrefs

    def test_a_gradient_whose_children_are_all_hidden_is_not_said_to_be_unused(
        self, document, page_records, hide
    ):
        hide(page_records["child"])

        page = document(page_records["gradient"])

        children = page.find("data-heat-flow", "children")
        assert children.attrs["data-hidden"] == "1"
        assert "data-state" not in children.attrs

    def test_a_hidden_interval_and_site_are_not_linked(
        self, document, page_records, hide
    ):
        hide(page_records["interval"])
        hide(page_records["site"])

        page = document(page_records["gradient"])

        for name in ("interval", "site"):
            assert page.find("data-heat-flow", name).attrs["data-state"] == "hidden"
        assert page_records["interval"].get_absolute_url() not in page.root.hrefs
        assert page_records["site"].get_absolute_url() not in page.root.hrefs

    def test_a_member_of_the_dataset_is_shown_the_hidden_child(
        self, document, page_records, published_dataset, hide, member
    ):
        (concealed,) = add_users(page_records, published_dataset, 1)
        hide(concealed)

        page = document(page_records["gradient"], user=member)

        children = page.find("data-heat-flow", "children")
        assert link_to(children, concealed)
        assert "data-hidden" not in children.attrs


class TestGradientPageKeepsFairDMsPage:
    def test_it_keeps_the_identifiers_and_citation_cards(self, document, page_records):
        page = document(page_records["gradient"])

        assert page.find("data-card", "identifiers") is not None
        assert page.find("data-card", "citation") is not None

    def test_a_dataset_manager_is_shown_the_manage_menu(self, document, page_records):
        manager = PersonFactory(is_claimed=True, password="test-pass-123")
        ContributionFactory(
            contributor=manager,
            content_object=page_records["gradient"].dataset,
            level=ContributionLevel.MANAGE,
        )

        page = document(page_records["gradient"], user=manager)

        assert page.find("data-menu", "manage") is not None

    def test_a_visitor_is_not_shown_the_manage_menu(self, document, page_records):
        assert document(page_records["gradient"]).find("data-menu", "manage") is None


class TestGradientPageQueries:
    def test_the_page_makes_the_same_queries_for_one_child_and_for_three(
        self, client, page_records, published_dataset
    ):
        url = page_records["gradient"].get_absolute_url()

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
    """The gradient's own quality card, moved from FS-007's measurement page tests."""

    def test_a_gradient_shows_its_own_score(self, page, gradient):
        card = page(gradient)

        assert card.cards == ["gradient"]
        assert card.hooks["own"].value == shown(gradient.score)
        assert card.hooks["scheme"].value == gradient.quality_scheme

    def test_a_score_that_is_not_determined_is_not_shown_as_zero(self, page, db):
        site = HeatFlowSiteFactory(explo_method="unspecified")
        gradient = ThermalGradientFactory(
            sample=HeatFlowIntervalFactory(site=site), method_top=[], method_bottom=[]
        )
        gradient.refresh_from_db()
        assert gradient.score is None

        card = page(gradient)

        assert card.hooks["own"].state == "not-determined"
        assert card.hooks["own"].value in ("", None)
        assert card.hooks["own"].text.strip() not in ("", "0", "0.0")

    def test_a_measurement_of_another_type_shows_its_own_card_not_the_gradients(
        self, page, db
    ):
        parent = ParentHeatFlowFactory()

        card = page(parent)

        assert card.cards == ["parent"]

    def test_the_placeholder_alert_is_gone(self, page, child):
        assert page(child).alerts == 0
