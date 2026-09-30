"""Receivers that keep stored quality scores current (FS-007).

A score is stored, never calculated when read, so it is refreshed when an input is written.
Every refresh writes with a queryset ``update``, which sends no signal, so a receiver never
re-enters itself.
"""

import weakref
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import ClassVar

from django.db import transaction


class _OnCommit:
    """The one callback registered for a transaction, so that it can be told from none."""

    def __call__(self) -> None:
        Recalculation.flush()


class Recalculation:
    """Decides which stored scores to refresh when an input changes.

    A refresh cascades in the order the scores are read: gradients and conductivities
    first, then the children that use them, then those children's parents, so that each
    level reads fresh values below it. A request names the records that changed. Made on
    its own it refreshes at once, and when deferred, or when it comes from a delete, it is
    collected and refreshed once when the deferral ends or the transaction commits.
    """

    _collected: ClassVar[dict[str, set[int]]] = {
        "gradients": set(),
        "conductivities": set(),
        "children": set(),
        "parents": set(),
    }
    # Weakly held, so a callback dropped by a rolled-back transaction counts as not scheduled.
    _scheduled: ClassVar[weakref.ref | None] = None
    _deferred: ClassVar[ContextVar[bool]] = ContextVar(
        "heat_flow_recalculation_deferred", default=False
    )

    @classmethod
    def request(
        cls,
        *,
        gradients: Iterable[int] = (),
        conductivities: Iterable[int] = (),
        children: Iterable[int] = (),
        parents: Iterable[int] = (),
        when_committed: bool = False,
    ) -> None:
        """Refresh the named records and everything that reads them, or collect them.

        Args:
            gradients: Pks of the ``ThermalGradient`` records that changed.
            conductivities: Pks of the ``IntervalConductivity`` records that changed.
            children: Pks of the ``HeatFlow`` records that changed.
            parents: Pks of the ``ParentHeatFlow`` records that changed.
            when_committed: Hold the refresh back until the transaction commits, because
                the records may be deleted by it. A delete always passes this.
        """
        named = {
            "gradients": set(gradients),
            "conductivities": set(conductivities),
            "children": set(children),
            "parents": set(parents),
        }
        if not cls._deferred.get() and not when_committed:
            cls._refresh(named)
            return
        for key, pks in named.items():
            cls._collected[key] |= pks
        if not cls._deferred.get():
            cls._schedule()

    @classmethod
    def measurement(cls, instance, *, when_committed: bool = False) -> None:
        """Request the refresh of a gradient or a conductivity and what reads it.

        Args:
            instance: The ``ThermalGradient`` or ``IntervalConductivity`` that changed.
            when_committed: Hold the refresh back until the transaction commits.
        """
        from .models import ThermalGradient

        key = "gradients" if isinstance(instance, ThermalGradient) else "conductivities"
        cls.request(**{key: [instance.pk]}, when_committed=when_committed)

    @classmethod
    def measurements_on(
        cls,
        interval_ids: Iterable[int],
        *,
        conductivities: bool = True,
        when_committed: bool = False,
    ) -> None:
        """Request the refresh of the gradients and conductivities on some intervals.

        Args:
            interval_ids: Pks of the ``HeatFlowInterval`` records whose depths, probe
                metadata or site changed.
            conductivities: Include the conductivities, which a probe's metadata does not
                touch.
            when_committed: Hold the refresh back until the transaction commits.
        """
        from .models import IntervalConductivity, ThermalGradient

        interval_ids = list(interval_ids)
        cls.request(
            gradients=ThermalGradient.objects.filter(
                sample_id__in=interval_ids
            ).values_list("pk", flat=True),
            conductivities=IntervalConductivity.objects.filter(
                sample_id__in=interval_ids if conductivities else []
            ).values_list("pk", flat=True),
            when_committed=when_committed,
        )

    @classmethod
    @contextmanager
    def deferred(cls) -> Iterator[None]:
        """Collect the requests made inside the block and refresh them once when it ends.

        The refresh runs on a normal exit only, so a block that fails leaves nothing
        collected and recalculation switched back on. A block inside another one joins it.
        """
        if cls._deferred.get():
            yield
            return
        token = cls._deferred.set(True)
        try:
            yield
        except BaseException:
            cls._take()
            raise
        finally:
            cls._deferred.reset(token)
        cls.flush()

    @classmethod
    def flush(cls) -> None:
        """Refresh everything collected, once each, and forget it."""
        cls._scheduled = None
        cls._refresh(cls._take())

    @classmethod
    def _take(cls) -> dict[str, set[int]]:
        """Return the collected pks and forget them."""
        taken = {key: pks.copy() for key, pks in cls._collected.items()}
        for pks in cls._collected.values():
            pks.clear()
        return taken

    @classmethod
    def _schedule(cls) -> None:
        """Register the refresh for the end of the current transaction, once."""
        if cls._scheduled is not None and cls._scheduled() is not None:
            return
        callback = _OnCommit()
        cls._scheduled = weakref.ref(callback)
        transaction.on_commit(callback)

    @staticmethod
    def _refresh(named: dict[str, set[int]]) -> None:
        """Refresh the named records that still exist, then what reads them.

        Args:
            named: The pks to refresh, under ``gradients``, ``conductivities``,
                ``children`` and ``parents``.
        """
        from django.db.models import Q

        from .models import (
            HeatFlow,
            IntervalConductivity,
            ParentHeatFlow,
            ThermalGradient,
        )

        for model, key in (
            (ThermalGradient, "gradients"),
            (IntervalConductivity, "conductivities"),
        ):
            for measurement in model.objects.filter(pk__in=named[key]):
                measurement.refresh_score()

        child_ids = named["children"] | set(
            HeatFlow.objects.filter(
                Q(thermal_gradient__in=named["gradients"])
                | Q(thermal_conductivity__in=named["conductivities"])
            ).values_list("pk", flat=True)
        )
        parent_ids = set(named["parents"])
        for child in HeatFlow.objects.filter(pk__in=child_ids):
            child.refresh_quality()
            if child.parent_id is not None:
                parent_ids.add(child.parent_id)

        for parent in ParentHeatFlow.objects.filter(pk__in=parent_ids):
            parent.refresh_quality()


def refresh_measurement_on_save(sender, instance, raw=False, **kwargs):
    """Refresh a gradient's or conductivity's score, its children and their parents on save.

    A fixture load (``raw``) writes rows before their relations exist, so it is left for the
    refresh command.
    """
    if raw:
        return
    Recalculation.measurement(instance)


def refresh_measurement_on_concepts(sender, instance, action, reverse, **kwargs):
    """Refresh a measurement and what reads it after a concept it reads is added, removed or cleared.

    Only the ``post_`` actions act, because ``pre_clear`` runs before the change and
    ``clear`` reports no pks. A change made from the concept's side (``reverse``) names no
    measurement instance and is ignored.
    """
    if reverse or action not in {"post_add", "post_remove", "post_clear"}:
        return
    Recalculation.measurement(instance)


def refresh_measurements_on_interval_save(sender, instance, raw=False, **kwargs):
    """Refresh the measurements on an interval when its depths change."""
    if raw:
        return
    Recalculation.measurements_on([instance.pk])


def refresh_measurements_on_probe_save(sender, instance, raw=False, **kwargs):
    """Refresh the gradients on the interval a probe's metadata describes when it is saved."""
    if raw:
        return
    Recalculation.measurements_on([instance.interval_id], conductivities=False)


def refresh_measurements_on_probe_delete(sender, instance, **kwargs):
    """Refresh the gradients on the interval of deleted probe metadata once the transaction commits.

    The refresh is held back because the interval may be deleted in the same transaction.
    """
    Recalculation.measurements_on(
        [instance.interval_id], conductivities=False, when_committed=True
    )


def refresh_measurements_on_site_save(sender, instance, raw=False, **kwargs):
    """Refresh every measurement on a site's intervals when the site is saved.

    The elevation gives a probe gradient its water depth, and the exploration method selects
    the route a measurement is scored by.
    """
    if raw:
        return
    Recalculation.measurements_on(instance.intervals.values_list("pk", flat=True))


def remember_parent_before_save(sender, instance, raw=False, **kwargs):
    """Note the parent a child is leaving, so it can be refreshed after the move."""
    instance._previous_parent_id = (
        None
        if raw or instance._state.adding
        else sender.objects.filter(pk=instance.pk)
        .values_list("parent_id", flat=True)
        .first()
    )


def refresh_child_on_save(sender, instance, raw=False, **kwargs):
    """Refresh a child's scores and its parent's when it is saved.

    A child that moved from one parent to another also refreshes the parent it left.
    """
    if raw:
        return
    previous = getattr(instance, "_previous_parent_id", None)
    Recalculation.request(
        children=[instance.pk],
        parents=[] if previous in (None, instance.parent_id) else [previous],
    )


def refresh_parent_on_child_delete(sender, instance, **kwargs):
    """Refresh a deleted child's parent once the transaction that deleted it commits.

    The refresh is held back because the parent may be deleted in the same transaction.
    """
    Recalculation.request(
        parents=[] if instance.parent_id is None else [instance.parent_id],
        when_committed=True,
    )


def refresh_child_on_correction_save(sender, instance, raw=False, **kwargs):
    """Refresh a child's scores, and its parent's, when one of its corrections is saved."""
    if raw:
        return
    Recalculation.request(children=[instance.heat_flow_id])


def refresh_child_on_correction_delete(sender, instance, **kwargs):
    """Refresh a child's scores once the transaction that deleted a correction commits.

    The refresh is held back because the child may be deleted in the same transaction.
    """
    Recalculation.request(children=[instance.heat_flow_id], when_committed=True)
