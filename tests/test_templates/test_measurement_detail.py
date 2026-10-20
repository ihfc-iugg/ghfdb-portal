# Tests for the gradient and conductivity pages' quality card. The subject is the card's templates
# under ``templates/cotton/card/quality/``, not a Python module, so the directory is
# declared under ``non-mirror-paths`` in pyproject.toml.

import pytest

from tests.factories import (
    HeatFlowIntervalFactory,
    HeatFlowSiteFactory,
    ParentHeatFlowFactory,
    ThermalGradientFactory,
)

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.skip(
        reason=(
            "FairDM replaced the measurement page the quality card was placed on. "
            "The card returns with the portal's own measurement pages."
        )
    ),
]


def shown(score):
    """A stored score as the page writes it in ``data-value``."""
    return f"{score:.1f}"


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
