# Tests for the parent heat flow value's overview page, read through its URL. The page's
# content is found by the ``data-`` hooks its templates carry, never by wording. Mirrors
# no Python module: the subject is the templates under ``project/heat_flow/templates/``
# and ``templates/cotton/``, declared under ``non-mirror-paths`` in pyproject.toml.

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from fairdm.contrib.contributors.choices import ContributionLevel
from fairdm.factories import ContributionFactory, PersonFactory
from heat_flow.models import ParentHeatFlow
from heat_flow.overview import HeatFlowPage

from tests.factories import HeatFlowFactory

pytestmark = pytest.mark.django_db

SHOW_ALL = "?show=all#children"


def link_to(node, record):
    """Say whether ``node`` links to ``record``'s page."""
    return record.get_absolute_url() in node.hrefs


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


def rows(page):
    """The children the page lists, by primary key, each with its row."""
    children = page.find("data-heat-flow", "children")
    return {
        int(row.attrs["data-child"]): row for row in children.find_all("data-child")
    }


@pytest.fixture
def small_cut(monkeypatch):
    """Cut a list of children at two."""
    monkeypatch.setattr(HeatFlowPage, "children_shown", 2)


class TestParentPage:
    def test_it_lists_every_child_linked_with_its_value_quality_code_and_relevance(
        self, document, page_records, published_dataset
    ):
        relevant = add_children(page_records, published_dataset, 2, is_relevant=True)
        (other,) = add_children(page_records, published_dataset, 1)

        page = document(page_records["parent"])

        listed = rows(page)
        everyone = [page_records["child"], other, *relevant]
        assert set(listed) == {child.pk for child in everyone}
        for child in everyone:
            child.refresh_from_db()
            row = listed[child.pk]
            assert link_to(row, child)
            assert child.print_value() in row.text
            assert row.find("data-quality", "code").attrs["data-value"] == (
                child.quality or ""
            )
            assert row.attrs["data-relevant"] == str(child.is_relevant).lower()

    def test_it_marks_the_relevant_children_as_what_the_quality_rests_on(
        self, document, page_records, published_dataset
    ):
        relevant = add_children(page_records, published_dataset, 2, is_relevant=True)
        add_children(page_records, published_dataset, 1)

        page = document(page_records["parent"])

        resting = {
            pk for pk, row in rows(page).items() if row.attrs["data-rests-on"] == "true"
        }
        assert resting == {child.pk for child in relevant}
        basis = page.find("data-quality-card", "parent").find("data-quality", "basis")
        assert basis.attrs["data-value"] == "relevant"

    def test_an_only_child_is_what_the_quality_rests_on_relevant_or_not(
        self, document, page_records
    ):
        child = page_records["child"]
        assert child.is_relevant is False

        page = document(page_records["parent"])

        assert rows(page)[child.pk].attrs["data-rests-on"] == "true"
        basis = page.find("data-quality-card", "parent").find("data-quality", "basis")
        assert basis.attrs["data-value"] == "single"

    def test_several_children_and_none_relevant_say_the_quality_is_not_determined(
        self, document, page_records, published_dataset
    ):
        add_children(page_records, published_dataset, 1)

        page = document(page_records["parent"])

        basis = page.find("data-quality-card", "parent").find("data-quality", "basis")
        assert basis.attrs["data-value"] == "none"
        assert {row.attrs["data-rests-on"] for row in rows(page).values()} == {"false"}

    def test_a_parent_with_no_children_says_the_quality_is_not_determined(
        self, document, page_records
    ):
        page_records["child"].delete()

        page = document(page_records["parent"])

        basis = page.find("data-quality-card", "parent").find("data-quality", "basis")
        assert basis.attrs["data-value"] == "empty"
        assert page.find("data-heat-flow", "children").attrs["data-state"] == "empty"

    def test_it_links_the_site_the_parent_represents(self, document, page_records):
        page = document(page_records["parent"])

        site = page.find("data-heat-flow", "site")
        assert "data-state" not in site.attrs
        assert link_to(site, page_records["site"])

    def test_it_shows_the_designation_fields(self, document, page_records):
        parent = page_records["parent"]
        ParentHeatFlow.objects.filter(pk=parent.pk).update(
            corr_HP_flag=True, comment="A curator's note.", ghfdb_id=4711
        )
        parent.refresh_from_db()

        page = document(parent)

        assert "data-state" not in page.find("data-field", "corr_HP_flag").attrs
        assert "A curator's note." in page.find("data-field", "comment").text
        assert "4711" in page.find("data-field", "ghfdb_id").text

    @pytest.mark.parametrize("flag", [True, False])
    def test_a_decided_heat_production_correction_is_recorded_either_way(
        self, document, page_records, flag
    ):
        parent = page_records["parent"]
        ParentHeatFlow.objects.filter(pk=parent.pk).update(corr_HP_flag=flag)
        parent.refresh_from_db()

        page = document(parent)

        assert "data-state" not in page.find("data-field", "corr_HP_flag").attrs

    def test_a_field_with_nothing_recorded_says_it_is_not_recorded(
        self, document, page_records
    ):
        parent = page_records["parent"]
        ParentHeatFlow.objects.filter(pk=parent.pk).update(
            corr_HP_flag=None, comment=None, ghfdb_id=4711
        )
        parent.refresh_from_db()

        page = document(parent)

        for name in ("corr_HP_flag", "comment"):
            assert page.find("data-field", name).attrs["data-state"] == "not-recorded"
        assert "data-state" not in page.find("data-field", "ghfdb_id").attrs


class TestParentPageQualityCard:
    def test_it_shows_the_stored_grades_code_revision_and_flags(
        self, document, page_records
    ):
        parent = page_records["parent"]
        ParentHeatFlow.objects.filter(pk=parent.pk).update(
            U_score="U2",
            M_score="M3x",
            quality="U2.M3x.-e-PX--",
            quality_scheme="hfqa_tool 0.2",
        )
        parent.refresh_from_db()

        card = document(parent).find("data-quality-card", "parent")

        assert card.find("data-quality", "u").attrs["data-value"] == "U2"
        assert card.find("data-quality", "m").attrs["data-value"] == "M3x"
        assert card.find("data-quality", "m").attrs["data-missing"] == "true"
        assert card.find("data-quality", "code").attrs["data-value"] == (
            "U2.M3x.-e-PX--"
        )
        assert card.find("data-quality", "scheme").attrs["data-value"] == (
            "hfqa_tool 0.2"
        )
        flags = "".join(
            card.find("data-quality", f"flag-{letter}").attrs["data-value"]
            for letter in "SETPVCR"
        )
        assert flags == "-e-PX--"

    def test_a_parent_not_yet_scored_is_not_determined_rather_than_zero(
        self, document, page_records
    ):
        parent = page_records["parent"]
        ParentHeatFlow.objects.filter(pk=parent.pk).update(
            U_score="Ux", M_score="Mx", quality=None, quality_scheme=""
        )
        parent.refresh_from_db()

        card = document(parent).find("data-quality-card", "parent")

        for name in ("u", "m", "code", "scheme"):
            assert card.find("data-quality", name).attrs["data-state"] == (
                "not-determined"
            )

    def test_a_stale_scheme_revision_is_said_to_be_stale(self, document, page_records):
        parent = page_records["parent"]
        ParentHeatFlow.objects.filter(pk=parent.pk).update(
            quality_scheme="hfqa_tool 0.1"
        )
        parent.refresh_from_db()

        assert document(parent).find("data-state", "stale") is not None

    def test_the_current_scheme_revision_is_not_said_to_be_stale(
        self, document, page_records
    ):
        parent = page_records["parent"]
        ParentHeatFlow.objects.filter(pk=parent.pk).update(
            quality_scheme="hfqa_tool 0.2"
        )
        parent.refresh_from_db()

        assert document(parent).find("data-state", "stale") is None


class TestParentPageCutList:
    def test_it_shows_the_cut_and_says_how_many_more(
        self, document, page_records, published_dataset, small_cut
    ):
        add_children(page_records, published_dataset, 2)

        page = document(page_records["parent"])

        assert len(rows(page)) == 2
        assert page.find("data-heat-flow", "children").attrs["data-more"] == "1"

    def test_it_links_to_the_same_page_asking_for_all_of_them(
        self, document, page_records, published_dataset, small_cut
    ):
        add_children(page_records, published_dataset, 2)

        page = document(page_records["parent"])

        assert SHOW_ALL in page.find("data-heat-flow", "children").hrefs

    def test_show_all_lists_every_child_and_drops_the_link(
        self, document, page_records, published_dataset, small_cut
    ):
        add_children(page_records, published_dataset, 2)

        page = document(page_records["parent"], show="all")

        children = page.find("data-heat-flow", "children")
        assert len(rows(page)) == 3
        assert "data-more" not in children.attrs
        assert SHOW_ALL not in children.hrefs

    def test_a_parent_within_the_cut_has_no_remainder(self, document, page_records):
        page = document(page_records["parent"])

        children = page.find("data-heat-flow", "children")
        assert "data-more" not in children.attrs
        assert SHOW_ALL not in children.hrefs


class TestParentPageForARecordTheVisitorMayNotOpen:
    def test_a_hidden_child_is_counted_and_never_linked(
        self, document, page_records, published_dataset, hide
    ):
        (concealed,) = add_children(page_records, published_dataset, 1)
        hide(concealed)

        page = document(page_records["parent"])

        children = page.find("data-heat-flow", "children")
        assert children.attrs["data-hidden"] == "1"
        assert link_to(children, page_records["child"])
        assert concealed.get_absolute_url() not in page.root.hrefs

    def test_a_parent_whose_children_are_all_hidden_is_not_said_to_have_none(
        self, document, page_records, hide
    ):
        hide(page_records["child"])

        page = document(page_records["parent"])

        children = page.find("data-heat-flow", "children")
        assert children.attrs["data-hidden"] == "1"
        assert "data-state" not in children.attrs

    def test_a_hidden_site_is_not_linked(self, document, page_records, hide):
        hide(page_records["site"])

        page = document(page_records["parent"])

        assert page.find("data-heat-flow", "site").attrs["data-state"] == "hidden"
        assert page_records["site"].get_absolute_url() not in page.root.hrefs

    def test_a_member_of_the_dataset_is_shown_the_hidden_child(
        self, document, page_records, published_dataset, hide, member
    ):
        (concealed,) = add_children(page_records, published_dataset, 1)
        hide(concealed)

        page = document(page_records["parent"], user=member)

        children = page.find("data-heat-flow", "children")
        assert link_to(children, concealed)
        assert "data-hidden" not in children.attrs


class TestParentPageKeepsFairDMsPage:
    def test_it_keeps_the_identifiers_and_citation_cards(self, document, page_records):
        page = document(page_records["parent"])

        assert page.find("data-card", "identifiers") is not None
        assert page.find("data-card", "citation") is not None

    def test_a_dataset_manager_is_shown_the_manage_menu(self, document, page_records):
        manager = PersonFactory(is_claimed=True, password="test-pass-123")
        ContributionFactory(
            contributor=manager,
            content_object=page_records["parent"].dataset,
            level=ContributionLevel.MANAGE,
        )

        page = document(page_records["parent"], user=manager)

        assert page.find("data-menu", "manage") is not None

    def test_a_visitor_is_not_shown_the_manage_menu(self, document, page_records):
        assert document(page_records["parent"]).find("data-menu", "manage") is None


class TestParentPageQueries:
    def test_the_page_makes_the_same_queries_for_one_child_and_for_three(
        self, client, page_records, published_dataset
    ):
        url = page_records["parent"].get_absolute_url()

        def count():
            with CaptureQueriesContext(connection) as queries:
                assert client.get(url).status_code == 200
            return len(queries)

        count()
        with_one = count()
        add_children(page_records, published_dataset, 2)

        with_three = count()

        assert with_three == with_one
