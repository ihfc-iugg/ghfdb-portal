"""Receivers that keep stored quality scores current (FS-007).

A score is stored, never calculated when read, so it is refreshed when an input is written.
Every refresh writes with a queryset ``update``, which sends no signal, so a receiver never
re-enters itself.
"""

from typing import ClassVar

from django.db import connection, transaction


class Recalculation:
    """Decides which stored scores to refresh when an input changes.

    Later stories extend the cascade to the children that use a measurement. For now it
    covers a measurement, a child's own scores and the parent a child rests under.
    """

    # Children whose correction was deleted, and parents that lost a child, refreshed
    # together once the deleting transaction commits. Deleting a dataset cascades through
    # every correction and child, so refreshing inline would rescore once per row.
    _deleted_correction_children: ClassVar[set[int]] = set()
    _deleted_child_parents: ClassVar[set[int]] = set()

    @staticmethod
    def measurement(instance) -> None:
        """Refresh a gradient's or conductivity's own score.

        Args:
            instance: The ``ThermalGradient`` or ``IntervalConductivity`` that changed.
        """
        instance.refresh_score()

    @staticmethod
    def child(instance) -> None:
        """Refresh a child's own scores and quality code, then its parent's.

        Args:
            instance: The ``HeatFlow`` whose input changed.
        """
        instance.refresh_quality()
        if instance.parent_id is not None:
            instance.parent.refresh_quality()

    @staticmethod
    def parent(parent_id: int | None) -> None:
        """Refresh the parent a child left, if it still exists.

        Args:
            parent_id: The pk of the parent, or ``None`` when the child had none.
        """
        from .models import ParentHeatFlow

        for parent in ParentHeatFlow.objects.filter(pk=parent_id):
            parent.refresh_quality()

    @classmethod
    def child_after_correction_deleted(cls, child_id: int) -> None:
        """Collect a child to refresh when the transaction commits.

        Args:
            child_id: The pk of the child whose correction was deleted.
        """
        cls._deleted_correction_children.add(child_id)
        cls._refresh_on_commit()

    @classmethod
    def parent_after_child_deleted(cls, parent_id: int | None) -> None:
        """Collect the parent of a deleted child to refresh when the transaction commits.

        Args:
            parent_id: The pk of the deleted child's parent, or ``None``.
        """
        if parent_id is not None:
            cls._deleted_child_parents.add(parent_id)
            cls._refresh_on_commit()

    @classmethod
    def _refresh_on_commit(cls) -> None:
        """Schedule one collected refresh for the end of the current transaction."""
        if not any(
            entry[1] == cls.refresh_collected for entry in connection.run_on_commit
        ):
            transaction.on_commit(cls.refresh_collected)

    @classmethod
    def refresh_collected(cls) -> None:
        """Refresh the collected children and parents that still exist."""
        from .models import HeatFlow

        child_ids = cls._deleted_correction_children.copy()
        cls._deleted_correction_children.difference_update(child_ids)
        parent_ids = cls._deleted_child_parents.copy()
        cls._deleted_child_parents.difference_update(parent_ids)
        for child in HeatFlow.objects.filter(pk__in=child_ids):
            cls.child(child)
        for parent_id in parent_ids:
            cls.parent(parent_id)


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
    Recalculation.child(instance)
    previous = getattr(instance, "_previous_parent_id", None)
    if previous is not None and previous != instance.parent_id:
        Recalculation.parent(previous)


def refresh_parent_on_child_delete(sender, instance, **kwargs):
    """Refresh a deleted child's parent once the transaction that deleted it commits.

    The refresh is held back because the parent may be deleted in the same transaction.
    """
    Recalculation.parent_after_child_deleted(instance.parent_id)


def refresh_child_on_correction_save(sender, instance, raw=False, **kwargs):
    """Refresh a child's scores, and its parent's, when one of its corrections is saved."""
    if raw:
        return
    Recalculation.child(instance.heat_flow)


def refresh_child_on_correction_delete(sender, instance, **kwargs):
    """Refresh a child's scores once the transaction that deleted a correction commits.

    The refresh is held back because the child may be deleted in the same transaction.
    """
    Recalculation.child_after_correction_deleted(instance.heat_flow_id)
