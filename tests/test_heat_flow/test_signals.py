# Tests for the receivers that keep stored scores current. Mirrors
# ``project/heat_flow/signals.py``.

import pytest
from django.db.models.signals import m2m_changed, post_save
from heat_flow import vocabularies
from research_vocabs.models import Concept

from tests.factories import (
    HeatFlowIntervalFactory,
    HeatFlowSiteFactory,
    IntervalConductivityFactory,
    ThermalGradientFactory,
)

pytestmark = pytest.mark.django_db


class SignalCounter:
    """Counts the signals sent while it is connected."""

    def __init__(self, signal, sender):
        self.signal = signal
        self.sender = sender
        self.calls = 0

    def __call__(self, **kwargs):
        self.calls += 1

    def __enter__(self):
        self.signal.connect(self, sender=self.sender, weak=False)
        return self

    def __exit__(self, *exc):
        self.signal.disconnect(self, sender=self.sender)


def borehole_gradient(**fields):
    site = HeatFlowSiteFactory(explo_method="drilling")
    interval = HeatFlowIntervalFactory(site=site, top=0, bottom=500)
    fields.setdefault("method_top", [])
    fields.setdefault("method_bottom", [])
    return ThermalGradientFactory(sample=interval, number=10, **fields)


def concept(vocabulary, name):
    return Concept.get_for_vocabulary(vocabulary).get(name=name)


class TestMeasurementReceivers:
    def test_saving_a_gradient_saves_it_once(self):
        from heat_flow.models import ThermalGradient

        gradient = borehole_gradient()

        with SignalCounter(post_save, ThermalGradient) as saves:
            gradient.save()

        assert saves.calls == 1

    def test_refreshing_a_score_sends_no_save_signal(self):
        from heat_flow.models import ThermalGradient

        gradient = borehole_gradient()

        with SignalCounter(post_save, ThermalGradient) as saves:
            gradient.refresh_score()

        assert saves.calls == 0

    def test_a_concept_change_refreshes_without_saving_the_record_again(self):
        from heat_flow.models import ThermalGradient

        gradient = borehole_gradient()
        logs = concept(vocabularies.TemperatureMethod, "LOGeq")

        with SignalCounter(post_save, ThermalGradient) as saves:
            gradient.method_top.add(logs)

        assert saves.calls == 0
        assert ThermalGradient.objects.get(pk=gradient.pk).score is not None

    def test_a_concept_field_the_score_does_not_read_leaves_it_alone(self):
        from heat_flow.models import ThermalGradient

        gradient = borehole_gradient()
        ThermalGradient.objects.filter(pk=gradient.pk).update(score=0.123)

        gradient.correction_top.add(
            concept(vocabularies.TemperatureCorrection, "hornerPlot")
        )

        assert ThermalGradient.objects.get(pk=gradient.pk).score == pytest.approx(
            0.123
        )

    def test_a_conductivity_field_the_score_does_not_read_leaves_it_alone(self):
        from heat_flow.models import IntervalConductivity

        site = HeatFlowSiteFactory(explo_method="drilling")
        conductivity = IntervalConductivityFactory(
            sample=HeatFlowIntervalFactory(site=site, top=0, bottom=500)
        )
        IntervalConductivity.objects.filter(pk=conductivity.pk).update(score=0.123)

        conductivity.strategy.add(
            concept(vocabularies.ConductivityStrategy, "random")
        )
        conductivity.pT_function.add(
            concept(vocabularies.ConductivityPTFunction, "unspecified")
        )

        assert IntervalConductivity.objects.get(
            pk=conductivity.pk
        ).score == pytest.approx(0.123)

    def test_the_concept_receiver_sends_no_further_m2m_signal(self):
        from heat_flow.models import ThermalGradient

        gradient = borehole_gradient()
        through = ThermalGradient.method_top.through

        with SignalCounter(m2m_changed, through) as changes:
            gradient.method_top.add(concept(vocabularies.TemperatureMethod, "LOGeq"))

        # One add sends one pre_add and one post_add, and the refresh adds no more.
        assert changes.calls == 2

    def test_a_fixture_load_does_not_score_the_record(self):
        from heat_flow.signals import refresh_measurement_on_save
        from heat_flow.models import ThermalGradient

        gradient = borehole_gradient()
        ThermalGradient.objects.filter(pk=gradient.pk).update(score=0.123)

        refresh_measurement_on_save(
            sender=ThermalGradient, instance=gradient, created=False, raw=True
        )

        assert ThermalGradient.objects.get(pk=gradient.pk).score == pytest.approx(
            0.123
        )
