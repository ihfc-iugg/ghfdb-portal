"""Receivers that keep stored quality scores current (FS-007).

A score is stored, never calculated when read, so it is refreshed when an input is written.
Every refresh writes with a queryset ``update``, which sends no signal, so a receiver never
re-enters itself.
"""

from typing import ClassVar

from django.db import connection, transaction


class Recalculation:
    """Decides which stored scores to refresh when an input changes.

    Later stories extend the cascade upward to the parents of a child and to the children
    that use a measurement. For now it covers a measurement and a child's own scores.
    """

    # Children whose correction was deleted, refreshed together once the deleting
    # transaction commits. Deleting a dataset cascades through every correction of every
    # child, so refreshing inline would rescore each child once per correction.
    _deleted_correction_children: ClassVar[set[int]] = set()

    @staticmethod
    def measurement(instance) -> None:
        """Refresh a gradient's or conductivity's own score.

        Args:
            instance: The ``ThermalGradient`` or ``IntervalConductivity`` that changed.
        """
        instance.refresh_score()

    @staticmethod
    def child(instance) -> None:
        """Refresh a child's own scores and quality code.

        Args:
            instance: The ``HeatFlow`` whose input changed.
        """
        instance.refresh_quality()

    @classmethod
    def child_after_correction_deleted(cls, child_id: int) -> None:
        """Collect a child to refresh when the transaction commits.

        Args:
            child_id: The pk of the child whose correction was deleted.
        """
        cls._deleted_correction_children.add(child_id)
        if not any(
            entry[1] == cls.refresh_collected for entry in connection.run_on_commit
        ):
            transaction.on_commit(cls.refresh_collected)

    @classmethod
    def refresh_collected(cls) -> None:
        """Refresh the collected children that still exist."""
        from .models import HeatFlow

        child_ids = cls._deleted_correction_children.copy()
        cls._deleted_correction_children.difference_update(child_ids)
        for child in HeatFlow.objects.filter(pk__in=child_ids):
            cls.child(child)


def refresh_measurement_on_save(sender, instance, raw=False, **kwargs):
    """Refresh a gradient's or conductivity's score when it is saved.

    A fixture load (``raw``) writes rows before their relations exist, so it is left for the
    refresh command.
    """
    if raw:
        return
    Recalculation.measurement(instance)


def refresh_measurement_on_concepts(sender, instance, action, reverse, **kwargs):
    """Refresh a measurement's score after a concept it reads is added, removed or cleared.

    Only the ``post_`` actions act, because ``pre_clear`` runs before the change and
    ``clear`` reports no pks. A change made from the concept's side (``reverse``) names no
    measurement instance and is ignored.
    """
    if reverse or action not in {"post_add", "post_remove", "post_clear"}:
        return
    Recalculation.measurement(instance)


def refresh_child_on_save(sender, instance, raw=False, **kwargs):
    """Refresh a child's scores when it is saved, and only the child (never its parent)."""
    if raw:
        return
    Recalculation.child(instance)


def refresh_child_on_correction_save(sender, instance, raw=False, **kwargs):
    """Refresh a child's scores when one of its corrections is saved."""
    if raw:
        return
    Recalculation.child(instance.heat_flow)


def refresh_child_on_correction_delete(sender, instance, **kwargs):
    """Refresh a child's scores once the transaction that deleted a correction commits.

    The refresh is held back because the child may be deleted in the same transaction.
    """
    Recalculation.child_after_correction_deleted(instance.heat_flow_id)
