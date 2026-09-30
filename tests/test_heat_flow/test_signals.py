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


# --- Keeping every score current (FS-007 US4) -------------------------------------------

BOREHOLE = dict(
    gradient=dict(number=10, top=("LOGeq",), bottom=("LOGeq",)),
    conductivity=dict(
        number=30,
        source=("core_samples",),
        location=("actual",),
        saturation=("saturatedMeasured",),
        pT=("actualInSitu",),
    ),
)
PROBE = dict(
    gradient=dict(number=6),
    conductivity=dict(
        number=4,
        source=("insitu_probe",),
        location=("actual",),
        method=("probePulse",),
        saturation=("saturatedInSitu",),
        pT=("actualInSitu",),
    ),
)


class Network:
    """One interval with a gradient and a conductivity, a child using both and its parent."""

    def __init__(self, explo_method="drilling", *, top=0, bottom=1000, **interval):
        from tests.factories import HeatFlowFactory, ParentHeatFlowFactory
        from tests.test_heat_flow.test_quality import (
            build_conductivity,
            build_gradient,
            build_interval,
        )

        inputs = PROBE if explo_method.startswith("probing") else BOREHOLE
        self.interval = build_interval(
            explo_method, top=top, bottom=bottom, **interval
        )
        self.site = self.interval.site
        self.gradient = build_gradient(self.interval, **inputs["gradient"])
        self.conductivity = build_conductivity(self.interval, **inputs["conductivity"])
        self.parent = ParentHeatFlowFactory(sample=self.site)
        self.child = self.child_using(self.gradient)

    def child_using(self, gradient):
        from tests.factories import HeatFlowFactory

        return HeatFlowFactory(
            sample=self.interval,
            thermal_gradient=gradient,
            thermal_conductivity=self.conductivity,
            parent=self.parent,
            is_relevant=True,
            value=70,
            uncertainty=7,
        )

    @property
    def records(self):
        return [self.gradient, self.conductivity, self.child, self.parent]

    def stored(self):
        """Every stored score of the network, keyed by record."""
        return {
            (type(record).__name__, record.pk): StoredScores.read(
                type(record).objects.get(pk=record.pk)
            )
            for record in self.records
        }


class StoredScores:
    """Recalculates every stored score in memory and finds those that differ (SC-004)."""

    FIELDS = {
        "ThermalGradient": ("score", "score_missing", "quality_scheme"),
        "IntervalConductivity": ("score", "score_missing", "quality_scheme"),
        "HeatFlow": (
            "U_score",
            "T_score",
            "T_score_missing",
            "TC_score",
            "TC_score_missing",
            "M_score",
            "quality",
            "quality_scheme",
        ),
        "ParentHeatFlow": ("U_score", "M_score", "quality", "quality_scheme"),
    }

    @classmethod
    def read(cls, record):
        return {
            name: getattr(record, name) for name in cls.FIELDS[type(record).__name__]
        }

    @classmethod
    def differing(cls):
        """List the records whose stored scores differ from a fresh calculation.

        The models write a refresh with a queryset ``update``, which is switched off here,
        so a refresh leaves the new values on the instance and the database untouched.
        """
        from unittest import mock

        from django.db.models.query import QuerySet
        from heat_flow.models import (
            HeatFlow,
            IntervalConductivity,
            ParentHeatFlow,
            ThermalGradient,
        )

        found = []
        with mock.patch.object(QuerySet, "update", return_value=1):
            for model in (
                ThermalGradient,
                IntervalConductivity,
                HeatFlow,
                ParentHeatFlow,
            ):
                for stored in model.objects.all():
                    fresh = model.objects.get(pk=stored.pk)
                    if isinstance(fresh, ParentHeatFlow | HeatFlow):
                        fresh.refresh_quality()
                    else:
                        fresh.refresh_score()
                    if cls.read(fresh) != cls.read(stored):
                        found.append((model.__name__, stored.pk))
        return found


class RefreshSpy:
    """Records every refresh made while it is active, by model name and pk."""

    METHODS = {
        "ThermalGradient": "refresh_score",
        "IntervalConductivity": "refresh_score",
        "HeatFlow": "refresh_quality",
        "ParentHeatFlow": "refresh_quality",
    }

    def __enter__(self):
        from unittest import mock

        import heat_flow.models as models

        self.calls = []
        self._patches = []
        for name, method in self.METHODS.items():
            model = getattr(models, name)
            original = getattr(model, method)

            def record(instance, *, _name=name, _original=original):
                self.calls.append((_name, instance.pk))
                _original(instance)

            patch = mock.patch.object(model, method, record)
            patch.start()
            self._patches.append(patch)
        return self

    def __exit__(self, *exc):
        for patch in self._patches:
            patch.stop()

    def of(self, *records):
        """The refreshes made to *records*, in the order they happened."""
        wanted = {(type(record).__name__, record.pk) for record in records}
        return [call for call in self.calls if call in wanted]

    def count(self, model_name):
        return len([call for call in self.calls if call[0] == model_name])


def keys(*records):
    return [(type(record).__name__, record.pk) for record in records]


def assert_moved(before, after, *records):
    """Every record's stored score differs from what it was."""
    for record in records:
        key = keys(record)[0]
        assert after[key] != before[key], f"{key} did not move"


class TestRecalculationTable:
    """Each row of the table: what depends on the input moves and the rest is left alone."""

    def test_a_measurement_saved_refreshes_its_children_and_their_parents(self):
        mine, other = Network(), Network()
        before = mine.stored()
        with RefreshSpy() as spy:
            mine.gradient.method_top.add(
                *concept_names(vocabularies.TemperatureMethod, "CPD")
            )

        assert spy.calls == keys(mine.gradient, mine.child, mine.parent)
        assert_moved(before, mine.stored(), mine.gradient, mine.child, mine.parent)
        assert spy.of(*other.records) == []
        assert StoredScores.differing() == []

    def test_a_shared_gradient_refreshes_every_child_using_it_and_the_parent_once(self):
        mine = Network()
        second = mine.child_using(mine.gradient)
        with RefreshSpy() as spy:
            mine.gradient.method_top.add(
                *concept_names(vocabularies.TemperatureMethod, "CPD")
            )

        assert spy.calls == keys(mine.gradient, mine.child, second, mine.parent)
        assert StoredScores.differing() == []

    def test_a_concept_removed_from_a_gradient_refreshes_what_uses_it(self):
        mine, other = Network(), Network()
        poor = concept_names(vocabularies.TemperatureMethod, "CPD")
        mine.gradient.method_top.add(*poor)
        before = mine.stored()
        with RefreshSpy() as spy:
            mine.gradient.method_top.remove(*poor)

        assert spy.calls == keys(mine.gradient, mine.child, mine.parent)
        assert_moved(before, mine.stored(), mine.gradient, mine.child)
        assert spy.of(*other.records) == []
        assert StoredScores.differing() == []

    def test_an_interval_saved_refreshes_the_measurements_on_it_and_onward(self):
        mine, other = Network(top=None, bottom=None), Network()
        before = mine.stored()
        mine.interval.top, mine.interval.bottom = 0, 1000
        with RefreshSpy() as spy:
            mine.interval.save()

        assert spy.calls == keys(
            mine.gradient, mine.conductivity, mine.child, mine.parent
        )
        assert_moved(before, mine.stored(), mine.conductivity, mine.child)
        assert spy.of(*other.records) == []
        assert StoredScores.differing() == []

    def test_probe_metadata_saved_refreshes_the_gradients_on_its_interval(self):
        mine, other = Network("probing_offshore", penetration=12, tilt=5), Network(
            "probing_offshore", penetration=12, tilt=5
        )
        before = mine.stored()
        probe = mine.interval.probe_metadata
        probe.penetration = 0.5
        with RefreshSpy() as spy:
            probe.save()

        assert spy.calls == keys(mine.gradient, mine.child, mine.parent)
        assert_moved(before, mine.stored(), mine.gradient, mine.child)
        assert spy.of(*other.records) == []
        assert StoredScores.differing() == []

    def test_probe_metadata_deleted_refreshes_the_gradients_on_its_interval(
        self, django_capture_on_commit_callbacks
    ):
        mine, other = Network("probing_offshore", penetration=12, tilt=5), Network(
            "probing_offshore", penetration=12, tilt=5
        )
        before = mine.stored()
        with RefreshSpy() as spy, django_capture_on_commit_callbacks(execute=True):
            mine.interval.probe_metadata.delete()

        assert spy.calls == keys(mine.gradient, mine.child, mine.parent)
        assert_moved(before, mine.stored(), mine.gradient, mine.child)
        assert spy.of(*other.records) == []
        assert StoredScores.differing() == []

    def test_a_site_elevation_changed_refreshes_every_measurement_on_its_intervals(
        self,
    ):
        mine, other = (
            Network("probing_offshore", elevation=-3000, penetration=12, tilt=5),
            Network("probing_offshore", elevation=-3000, penetration=12, tilt=5),
        )
        before = mine.stored()
        mine.site.elevation = -1000
        with RefreshSpy() as spy:
            mine.site.save()

        assert spy.calls == keys(
            mine.gradient, mine.conductivity, mine.child, mine.parent
        )
        assert_moved(before, mine.stored(), mine.gradient, mine.child)
        assert spy.of(*other.records) == []
        assert StoredScores.differing() == []

    def test_a_site_exploration_method_changed_refreshes_every_measurement_on_it(self):
        mine, other = Network(), Network()
        before = mine.stored()
        mine.site.explo_method = "other"
        with RefreshSpy() as spy:
            mine.site.save()

        assert spy.calls == keys(
            mine.gradient, mine.conductivity, mine.child, mine.parent
        )
        assert_moved(before, mine.stored(), mine.gradient, mine.conductivity)
        assert spy.of(*other.records) == []
        assert StoredScores.differing() == []


def concept_names(vocabulary, *names):
    from tests.test_heat_flow.test_quality import concepts

    return concepts(vocabulary, *names)


class TestDatasetDelete:
    def test_deleting_a_dataset_leaves_no_stale_parent_and_no_refresh_per_correction(
        self, django_capture_on_commit_callbacks
    ):
        from fairdm.factories import DatasetFactory
        from heat_flow.models import HeatFlow, ParentHeatFlow
        from tests.factories import HeatFlowCorrectionFactory, ParentHeatFlowFactory
        from tests.test_heat_flow.test_models.test_parent import child_of

        doomed, kept = DatasetFactory(), DatasetFactory()
        parent = ParentHeatFlowFactory(dataset=kept)
        child_of(parent, "U1", is_relevant=True)
        leaving = child_of(parent, "U4", is_relevant=True)
        HeatFlow.objects.filter(pk=leaving.pk).update(dataset=doomed)
        for kind in ("S", "E", "SUR", "T", "IS"):
            HeatFlowCorrectionFactory(heat_flow=leaving, correction_type=kind)
        assert ParentHeatFlow.objects.get(pk=parent.pk).U_score == "U4"

        with RefreshSpy() as spy, django_capture_on_commit_callbacks(execute=True):
            doomed.delete()

        assert not HeatFlow.objects.filter(pk=leaving.pk).exists()
        assert spy.count("HeatFlow") == 0
        assert spy.count("ParentHeatFlow") == 1
        assert ParentHeatFlow.objects.get(pk=parent.pk).U_score == "U1"
        assert StoredScores.differing() == []


class TestScheduledRefresh:
    def test_a_rolled_back_transaction_does_not_stop_the_next_one_scheduling(
        self, django_capture_on_commit_callbacks
    ):
        from django.db import transaction
        from tests.factories import HeatFlowCorrectionFactory

        mine = Network()
        first = HeatFlowCorrectionFactory(heat_flow=mine.child, correction_type="S")
        second = HeatFlowCorrectionFactory(heat_flow=mine.child, correction_type="E")

        with django_capture_on_commit_callbacks(execute=False) as callbacks:
            try:
                with transaction.atomic():
                    first.delete()
                    raise RuntimeError
            except RuntimeError:
                pass
            second.delete()

        assert len(callbacks) == 1


class TestRecordsLoadedFromTheDatabase:
    """The cascade and the refresh command score records they have just read back."""

    def test_a_measurement_read_back_scores_as_the_one_built_in_memory(self):
        mine = Network()
        for built in (mine.gradient, mine.conductivity):
            built.refresh_score()
            loaded = type(built).objects.get(pk=built.pk)

            loaded.refresh_score()

            assert built.score is not None
            assert (loaded.score, loaded.score_missing) == (
                built.score,
                built.score_missing,
            )

    def test_a_child_read_back_scores_as_the_one_built_in_memory(self):
        mine = Network()
        mine.child.refresh_quality()
        loaded = type(mine.child).objects.get(pk=mine.child.pk)

        loaded.refresh_quality()

        assert mine.child.T_score is not None
        assert loaded.quality == mine.child.quality


class TestDeferral:
    """``Recalculation.deferred()`` collects what changes and refreshes it once on exit."""

    def test_nothing_is_refreshed_inside_the_block_and_each_record_once_after_it(self):
        from heat_flow.signals import Recalculation

        mine = Network()
        with RefreshSpy() as spy:
            with Recalculation.deferred():
                mine.gradient.method_top.add(
                    *concept_names(vocabularies.TemperatureMethod, "CPD")
                )
                mine.gradient.save()
                mine.child.save()
                assert spy.calls == []

        assert spy.calls == keys(mine.gradient, mine.child, mine.parent)
        assert StoredScores.differing() == []

    def test_a_block_that_fails_leaves_recalculation_on_and_nothing_collected(self):
        from heat_flow.signals import Recalculation

        mine = Network()
        with pytest.raises(RuntimeError):
            with Recalculation.deferred():
                mine.gradient.save()
                raise RuntimeError

        with RefreshSpy() as spy:
            mine.gradient.save()
        assert spy.calls == keys(mine.gradient, mine.child, mine.parent)

    def test_a_block_inside_another_joins_it(self):
        from heat_flow.signals import Recalculation

        mine = Network()
        with RefreshSpy() as spy:
            with Recalculation.deferred():
                with Recalculation.deferred():
                    mine.gradient.save()
                assert spy.calls == []
                mine.conductivity.save()

        assert len(spy.calls) == len(set(spy.calls))
        assert spy.calls == keys(
            mine.gradient, mine.conductivity, mine.child, mine.parent
        )
