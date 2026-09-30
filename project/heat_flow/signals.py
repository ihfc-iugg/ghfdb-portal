"""Receivers that keep stored quality scores current (FS-007).

A score is stored, never calculated when read, so it is refreshed when an input is written.
Every refresh writes with a queryset ``update``, which sends no signal, so a receiver never
re-enters itself.
"""


class Recalculation:
    """Decides which stored scores to refresh when an input changes.

    Later stories extend the cascade upward to the children and parents that use a
    measurement. For now it covers the measurement itself.
    """

    @staticmethod
    def measurement(instance) -> None:
        """Refresh a gradient's or conductivity's own score.

        Args:
            instance: The ``ThermalGradient`` or ``IntervalConductivity`` that changed.
        """
        instance.refresh_score()


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
