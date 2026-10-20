# Tests for the child heat flow value's overview page, read through its URL. The page's
# content is found by the ``data-`` hooks its templates carry, never by wording. Mirrors
# no Python module: the subject is the templates under ``project/heat_flow/templates/`` and
# ``templates/cotton/``, declared under ``non-mirror-paths`` in pyproject.toml.

import pytest
from fairdm.contrib.contributors.choices import ContributionLevel
from fairdm.factories import ContributionFactory, PersonFactory
from heat_flow.models import HeatFlow, HeatFlowCorrection

from tests.factories import (
    HeatFlowCorrectionFactory,
    HeatFlowFactory,
)

pytestmark = pytest.mark.django_db


def shown(score):
    """A stored score as the page writes it in ``data-value``."""
    return f"{score:.1f}"


def link_to(node, record):
    """Say whether ``node`` links to ``record``'s page."""
    return record.get_absolute_url() in node.hrefs


class TestChildPage:
    def test_it_shows_the_gradient_and_conductivity_it_was_calculated_from_each_linked(
        self, document, page_records
    ):
        page = document(page_records["child"])

        gradient = page.find("data-heat-flow", "gradient")
        conductivity = page.find("data-heat-flow", "conductivity")
        assert link_to(gradient, page_records["gradient"])
        assert page_records["gradient"].print_value() in gradient.text
        assert link_to(conductivity, page_records["conductivity"])
        assert page_records["conductivity"].print_value() in conductivity.text

    def test_it_shows_the_childs_value_and_method(self, document, page_records):
        concept = page_records["child"].method.model.objects.first()
        page_records["child"].method.set([concept])

        page = document(page_records["child"])

        assert (
            page_records["child"].print_value() in page.find("data-field", "value").text
        )
        assert concept.label in page.find("data-field", "method").text

    def test_a_child_without_a_method_says_the_method_is_not_recorded(
        self, document, page_records
    ):
        page_records["child"].method.set([])

        page = document(page_records["child"])

        assert page.find("data-field", "method").attrs["data-state"] == "not-recorded"

    def test_it_shows_every_correction_with_its_type_and_status(
        self, document, page_records
    ):
        child = page_records["child"]
        recorded = {
            "SUR": "present_corrected",
            "S": "present_not_corrected",
            "E": "not_recognized",
        }
        for kind, status in recorded.items():
            HeatFlowCorrectionFactory(
                heat_flow=child, correction_type=kind, status=status
            )

        page = document(child)

        rows = page.find("data-heat-flow", "corrections").find_all("data-correction")
        assert {
            r.attrs["data-correction"]: r.attrs["data-status"] for r in rows
        } == recorded

    def test_a_child_with_no_corrections_says_none_are_recorded(
        self, document, page_records
    ):
        page = document(page_records["child"])

        corrections = page.find("data-heat-flow", "corrections")
        assert corrections.attrs["data-state"] == "empty"
        assert corrections.find_all("data-correction") == []

    def test_a_correction_recorded_as_not_recognised_is_shown_as_recorded(
        self, document, page_records
    ):
        HeatFlowCorrectionFactory(
            heat_flow=page_records["child"],
            correction_type="SUR",
            status=HeatFlowCorrection.StatusChoices.NOT_RECOGNIZED,
        )

        page = document(page_records["child"])

        corrections = page.find("data-heat-flow", "corrections")
        assert "data-state" not in corrections.attrs
        assert len(corrections.find_all("data-correction")) == 1

    def test_a_stale_scheme_revision_is_said_to_be_stale(self, document, page_records):
        child = page_records["child"]
        HeatFlow.objects.filter(pk=child.pk).update(quality_scheme="hfqa_tool 0.1")
        child.refresh_from_db()

        page = document(child)

        assert page.find("data-state", "stale") is not None

    def test_the_current_scheme_revision_is_not_said_to_be_stale(
        self, document, page_records
    ):
        child = page_records["child"]
        HeatFlow.objects.filter(pk=child.pk).update(quality_scheme="hfqa_tool 0.2")
        child.refresh_from_db()

        page = document(child)

        assert page.find("data-state", "stale") is None

    def test_it_links_the_parent_and_says_the_child_is_marked_relevant(
        self, document, page_records
    ):
        HeatFlow.objects.filter(pk=page_records["child"].pk).update(is_relevant=True)
        page_records["child"].refresh_from_db()

        page = document(page_records["child"])

        parent = page.find("data-heat-flow", "parent")
        assert link_to(parent, page_records["parent"])
        assert parent.attrs["data-relevant"] == "true"

    def test_it_says_when_the_child_is_not_marked_relevant(
        self, document, page_records
    ):
        HeatFlow.objects.filter(pk=page_records["child"].pk).update(is_relevant=False)
        page_records["child"].refresh_from_db()

        page = document(page_records["child"])

        assert page.find("data-heat-flow", "parent").attrs["data-relevant"] == "false"

    def test_it_links_the_depth_interval_and_the_site(self, document, page_records):
        page = document(page_records["child"])

        assert link_to(
            page.find("data-heat-flow", "interval"), page_records["interval"]
        )
        assert link_to(page.find("data-heat-flow", "site"), page_records["site"])

    def test_a_child_with_no_gradient_says_which_is_not_recorded_and_shows_the_rest(
        self, document, page_records
    ):
        HeatFlow.objects.filter(pk=page_records["child"].pk).update(
            thermal_gradient=None
        )
        page_records["child"].refresh_from_db()

        page = document(page_records["child"])

        assert (
            page.find("data-heat-flow", "gradient").attrs["data-state"]
            == "not-recorded"
        )
        assert "data-state" not in page.find("data-heat-flow", "conductivity").attrs
        assert link_to(
            page.find("data-heat-flow", "interval"), page_records["interval"]
        )

    def test_a_child_with_no_conductivity_says_which_is_not_recorded(
        self, document, page_records
    ):
        HeatFlow.objects.filter(pk=page_records["child"].pk).update(
            thermal_conductivity=None
        )
        page_records["child"].refresh_from_db()

        page = document(page_records["child"])

        conductivity = page.find("data-heat-flow", "conductivity")
        assert conductivity.attrs["data-state"] == "not-recorded"

    def test_a_child_with_no_parent_says_it_belongs_to_none(
        self, document, page_records
    ):
        HeatFlow.objects.filter(pk=page_records["child"].pk).update(parent=None)
        page_records["child"].refresh_from_db()

        page = document(page_records["child"])

        assert page.find("data-heat-flow", "parent").attrs["data-state"] == "none"

    def test_an_empty_field_is_shown_as_not_recorded(self, document, page_records):
        HeatFlow.objects.filter(pk=page_records["child"].pk).update(
            surface_temperature=None, expedition="Leg 12"
        )
        page_records["child"].refresh_from_db()

        page = document(page_records["child"])

        empty = page.find("data-field", "surface_temperature")
        assert empty.attrs["data-state"] == "not-recorded"
        filled = page.find("data-field", "expedition")
        assert "data-state" not in filled.attrs
        assert "Leg 12" in filled.text


class TestChildPageForARecordTheVisitorMayNotOpen:
    @pytest.mark.parametrize("name", ["gradient", "conductivity", "parent"])
    def test_a_hidden_record_is_neither_named_nor_linked(
        self, document, page_records, hide, name
    ):
        hide(page_records[name])

        page = document(page_records["child"])

        node = page.find("data-heat-flow", name)
        assert node.attrs["data-state"] == "hidden"
        assert not link_to(node, page_records[name])
        assert str(page_records[name].print_value()) not in node.text

    def test_a_hidden_interval_and_site_are_not_linked(
        self, document, page_records, hide
    ):
        hide(page_records["interval"])
        hide(page_records["site"])

        page = document(page_records["child"])

        for name in ("interval", "site"):
            node = page.find("data-heat-flow", name)
            assert node.attrs["data-state"] == "hidden"
            assert not link_to(node, page_records[name])

    def test_a_hidden_gradient_shows_no_score_in_the_quality_card(
        self, quality_hooks, page_records, hide
    ):
        before = quality_hooks(page_records["child"])
        assert before.hooks["t-own"].state == "determined"

        hide(page_records["gradient"])
        after = quality_hooks(page_records["child"])

        assert after.hooks["t-own"].state == "not-determined"
        assert after.hooks["t-own"].value == ""
        assert after.hooks["t-corrected"].state == before.hooks["t-corrected"].state

    def test_a_hidden_conductivity_shows_no_score_in_the_quality_card(
        self, quality_hooks, page_records, hide
    ):
        before = quality_hooks(page_records["child"])
        assert before.hooks["tc-own"].state == "determined"

        hide(page_records["conductivity"])
        after = quality_hooks(page_records["child"])

        assert after.hooks["tc-own"].state == "not-determined"
        assert after.hooks["tc-own"].value == ""

    def test_a_member_of_the_dataset_is_shown_the_hidden_gradient(
        self, document, page_records, hide, member
    ):
        hide(page_records["gradient"])

        page = document(page_records["child"], user=member)

        node = page.find("data-heat-flow", "gradient")
        assert "data-state" not in node.attrs
        assert link_to(node, page_records["gradient"])


class TestChildPageKeepsFairDMsPage:
    def test_it_keeps_the_identifiers_and_citation_cards(self, document, page_records):
        page = document(page_records["child"])

        assert page.find("data-card", "identifiers") is not None
        assert page.find("data-card", "citation") is not None

    def test_a_dataset_manager_is_shown_the_manage_menu(self, document, page_records):
        manager = PersonFactory(is_claimed=True, password="test-pass-123")
        ContributionFactory(
            contributor=manager,
            content_object=page_records["child"].dataset,
            level=ContributionLevel.MANAGE,
        )

        page = document(page_records["child"], user=manager)

        assert page.find("data-menu", "manage") is not None

    def test_a_visitor_is_not_shown_the_manage_menu(self, document, page_records):
        assert document(page_records["child"]).find("data-menu", "manage") is None


class TestChildCard:
    def test_a_corrected_score_is_shown_beside_the_gradients_own(self, page, child):
        own, corrected = child.thermal_gradient.score, child.T_score

        card = page(child)

        assert own != pytest.approx(corrected)
        assert card.hooks["t-own"].value == shown(own)
        assert card.hooks["t-corrected"].value == shown(corrected)

    def test_a_conductivity_is_shown_the_same_way(self, page, child):
        own, corrected = child.thermal_conductivity.score, child.TC_score

        card = page(child)

        assert card.hooks["tc-own"].value == shown(own)
        assert card.hooks["tc-corrected"].value == shown(corrected)

    def test_the_child_shows_its_grades_code_flags_and_revision(self, page, child):
        card = page(child)

        assert card.hooks["u"].value == child.U_score
        assert card.hooks["m"].value == child.M_score
        assert card.hooks["code"].value == child.quality
        assert card.hooks["scheme"].value == child.quality_scheme

    def test_each_of_the_seven_flags_shows_its_stored_character(self, page, child):
        card = page(child)

        shown_flags = "".join(
            card.hooks[f"flag-{letter}"].value for letter in "SETPVCR"
        )
        assert shown_flags == child.quality[-7:]
        # The bottom-water correction is the fifth flag, present and corrected.
        assert card.hooks["flag-V"].value == "V"

    def test_a_score_reached_with_missing_information_carries_a_text_mark(
        self, page, child
    ):
        assert child.TC_score_missing is True

        card = page(child)

        tc = card.hooks["tc-corrected"]
        assert tc.missing == "true"
        assert [mark.text.strip() for mark in tc.marks] != []
        assert all(mark.text.strip() for mark in tc.marks)

    def test_a_score_without_missing_information_carries_no_mark(self, page, child):
        assert child.T_score_missing is False

        card = page(child)

        assert card.hooks["t-corrected"].missing == "false"
        assert card.hooks["t-corrected"].marks == []

    def test_an_m_score_carrying_the_missing_mark_shows_it(self, page, child):
        assert child.M_score.endswith("x")

        card = page(child)

        m = card.hooks["m"]
        assert m.missing == "true"
        assert all(mark.text.strip() for mark in m.marks)
        assert m.marks

    def test_a_child_with_no_gradient_or_conductivity_is_not_determined(
        self, page, probe_interval
    ):
        child = HeatFlowFactory(
            sample=probe_interval, value=70, uncertainty=None, method=[]
        )
        child.refresh_from_db()

        card = page(child)

        for hook in ("t-own", "t-corrected", "tc-own", "tc-corrected", "m", "u"):
            assert card.hooks[hook].state == "not-determined"
            assert card.hooks[hook].text.strip() not in ("", "0", "0.0")
        for hook in ("t-own", "t-corrected", "tc-own", "tc-corrected"):
            assert card.hooks[hook].value == ""

    def test_a_child_that_has_not_been_scored_says_so(self, page, child):
        from heat_flow.models import HeatFlow

        HeatFlow.objects.filter(pk=child.pk).update(quality_scheme="", quality=None)
        child.refresh_from_db()

        card = page(child)

        assert card.hooks["scheme"].state == "not-determined"
        for letter in "SETPVCR":
            assert card.hooks[f"flag-{letter}"].value == "-"

    def test_the_page_makes_the_same_queries_for_any_number_of_corrections(
        self, query_count, child
    ):
        with_one = query_count(child)
        for kind in ("S", "E", "TOPO", "PAL", "CONV", "HR"):
            HeatFlowCorrectionFactory(
                heat_flow=child, correction_type=kind, status="present_corrected"
            )

        with_seven = query_count(child)

        assert with_seven == with_one
