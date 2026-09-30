# Tests for the measurement page's quality card. The subject is the template
# ``templates/measurement/detail.html``, not a Python module, so the directory is
# declared under ``non-mirror-paths`` in pyproject.toml.

import pytest

from tests.factories import (
    HeatFlowFactory,
    HeatFlowCorrectionFactory,
    HeatFlowIntervalFactory,
    HeatFlowSiteFactory,
    IntervalConductivityFactory,
    ParentHeatFlowFactory,
    ThermalGradientFactory,
)

pytestmark = pytest.mark.django_db


def shown(score):
    """A stored score as the page writes it in ``data-value``."""
    return f"{score:.1f}"


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

        shown_flags = "".join(card.hooks[f"flag-{letter}"].value for letter in "SETPVCR")
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


class TestMeasurementCard:
    def test_a_gradient_shows_its_own_score(self, page, gradient):
        card = page(gradient)

        assert card.cards == ["gradient"]
        assert card.hooks["own"].value == shown(gradient.score)
        assert card.hooks["scheme"].value == gradient.quality_scheme

    def test_a_conductivity_shows_its_own_score_and_its_mark(self, page, conductivity):
        card = page(conductivity)

        assert card.cards == ["conductivity"]
        assert card.hooks["own"].value == shown(conductivity.score)
        assert card.hooks["own"].missing == "true"
        assert card.hooks["own"].marks

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

    def test_a_measurement_of_another_type_shows_no_card(self, page, db):
        parent = ParentHeatFlowFactory()

        card = page(parent)

        assert card.cards == []

    def test_the_placeholder_alert_is_gone(self, page, child):
        assert page(child).alerts == 0
