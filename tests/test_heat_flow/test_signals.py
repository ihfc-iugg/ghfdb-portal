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


class TestChildReceivers:
    def child(self):
        from tests.factories import HeatFlowFactory

        site = HeatFlowSiteFactory(explo_method="drilling")
        interval = HeatFlowIntervalFactory(site=site, top=0, bottom=500)
        return HeatFlowFactory(sample=interval, value=70, uncertainty=7)

    def test_saving_a_child_saves_it_once(self):
        from heat_flow.models import HeatFlow

        child = self.child()

        with SignalCounter(post_save, HeatFlow) as saves:
            child.save()

        assert saves.calls == 1

    def test_refreshing_a_child_sends_no_save_signal(self):
        from heat_flow.models import HeatFlow, HeatFlowCorrection

        child = self.child()

        with (
            SignalCounter(post_save, HeatFlow) as child_saves,
            SignalCounter(post_save, HeatFlowCorrection) as correction_saves,
        ):
            child.refresh_quality()

        assert child_saves.calls == 0
        assert correction_saves.calls == 0

    def test_a_fixture_load_does_not_score_the_child(self):
        from heat_flow.models import HeatFlow
        from heat_flow.signals import refresh_child_on_save

        child = self.child()
        HeatFlow.objects.filter(pk=child.pk).update(quality="stale")

        refresh_child_on_save(sender=HeatFlow, instance=child, created=False, raw=True)

        assert HeatFlow.objects.get(pk=child.pk).quality == "stale"

    def test_deleting_several_corrections_of_a_child_schedules_one_refresh(
        self, django_capture_on_commit_callbacks
    ):
        from tests.factories import HeatFlowCorrectionFactory

        child = self.child()
        corrections = [
            HeatFlowCorrectionFactory(heat_flow=child, correction_type=kind)
            for kind in ("S", "E", "SUR")
        ]

        with django_capture_on_commit_callbacks(execute=False) as callbacks:
            for correction in corrections:
                correction.delete()

        assert len(callbacks) == 1


class TestParentReceivers:
    """A parent is refreshed by its children's changes and never by its own save."""

    @staticmethod
    def parent_with(*grades, is_relevant=True):
        from tests.factories import ParentHeatFlowFactory
        from tests.test_heat_flow.test_models.test_parent import child_of

        parent = ParentHeatFlowFactory()
        children = [child_of(parent, grade, is_relevant=is_relevant) for grade in grades]
        return parent, children

    @staticmethod
    def stored(parent):
        from heat_flow.models import ParentHeatFlow

        return ParentHeatFlow.objects.get(pk=parent.pk)

    def test_changing_a_childs_uncertainty_moves_its_parent(self):
        parent, (child,) = self.parent_with("U1")

        child.uncertainty = 40
        child.save()

        assert self.stored(parent).U_score == "U4"

    def test_marking_a_child_relevant_brings_it_into_the_parent(self):
        parent, _ = self.parent_with("U1", "U4", is_relevant=False)
        assert self.stored(parent).U_score == "Ux"
        child = parent.children.get(U_score="U4")

        child.is_relevant = True
        child.save()

        assert self.stored(parent).U_score == "U4"

    def test_moving_a_child_refreshes_both_parents(self):
        origin, (child,) = self.parent_with("U3")
        destination, _ = self.parent_with("U1")
        assert self.stored(origin).U_score == "U3"

        child.parent = destination
        child.save()

        assert self.stored(origin).quality == "Ux.Mx.-------"
        assert self.stored(destination).U_score == "U3"

    def test_detaching_a_child_refreshes_the_parent_it_left(self):
        parent, (child,) = self.parent_with("U3")

        child.parent = None
        child.save()

        assert self.stored(parent).quality == "Ux.Mx.-------"

    def test_deleting_the_last_child_leaves_the_parent_not_determined(
        self, django_capture_on_commit_callbacks
    ):
        parent, (child,) = self.parent_with("U2")
        assert self.stored(parent).U_score == "U2"

        with django_capture_on_commit_callbacks(execute=True):
            child.delete()

        assert self.stored(parent).quality == "Ux.Mx.-------"

    def test_deleting_one_of_several_children_refreshes_the_parent_from_the_rest(
        self, django_capture_on_commit_callbacks
    ):
        parent, (kept, dropped) = self.parent_with("U1", "U4")
        assert self.stored(parent).U_score == "U4"

        with django_capture_on_commit_callbacks(execute=True):
            dropped.delete()

        assert self.stored(parent).U_score == "U1"

    def test_deleting_children_schedules_one_refresh_on_commit(
        self, django_capture_on_commit_callbacks
    ):
        parent, children = self.parent_with("U1", "U2", "U3")

        with django_capture_on_commit_callbacks(execute=False) as callbacks:
            for child in children:
                child.delete()

        assert len(callbacks) == 1

    def test_a_parent_deleted_with_its_child_is_not_refreshed(
        self, django_capture_on_commit_callbacks
    ):
        from heat_flow.models import ParentHeatFlow

        parent, (child,) = self.parent_with("U2")

        with django_capture_on_commit_callbacks(execute=True):
            child.delete()
            parent.delete()

        assert not ParentHeatFlow.objects.filter(pk=parent.pk).exists()

    def test_a_correction_saved_on_a_child_moves_its_parents_flags(self):
        from tests.factories import HeatFlowCorrectionFactory

        parent, (child,) = self.parent_with("U2")

        HeatFlowCorrectionFactory(
            heat_flow=child, correction_type="S", status="present_corrected"
        )

        assert self.stored(parent).quality == "U2.Mx.S------"

    def test_a_correction_deleted_from_a_child_moves_its_parents_flags(
        self, django_capture_on_commit_callbacks
    ):
        from tests.factories import HeatFlowCorrectionFactory

        parent, (child,) = self.parent_with("U2")
        correction = HeatFlowCorrectionFactory(
            heat_flow=child, correction_type="S", status="present_corrected"
        )
        assert self.stored(parent).quality == "U2.Mx.S------"

        with django_capture_on_commit_callbacks(execute=True):
            correction.delete()

        assert self.stored(parent).quality == "U2.Mx.-------"

    def test_a_childs_save_sends_no_save_signal_for_its_parent(self):
        from django.db.models.signals import post_save
        from heat_flow.models import ParentHeatFlow

        _, (child,) = self.parent_with("U2")

        with SignalCounter(post_save, ParentHeatFlow) as saves:
            child.save()

        assert saves.calls == 0
