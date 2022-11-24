"""
A collection of functions that hook into Django's model signals.

For more information on signals, see
https://docs.djangoproject.com/en/3.2/topics/signals/
"""

from django.db.models.signals import m2m_changed, pre_save, post_save
from django.dispatch import receiver
from database.models import Interval


@receiver(post_save, sender=Interval)
def interval_changed(sender, instance, **kwargs):
    """Ensures that every time a `database.models.Interval`instance
    is saved, the associated reference will also be saved on the associated
    `database.models.HeatFlow`.

    Args:
        sender (_type_): database.models.Interval
        instance (_type_): database.models.Interval
    """
    # Preliminary test to update Site instance after modifying an Interval

    # Current updates the site acquisition date to the latest acquired
    # Interval and adds the interval reference to the site object
    site = instance.site
    # most_recent = site.intervals.order_by('-q_acq').first()

    # site.q_acq = most_recent.q_acq
    site.references.add(instance.reference)
    site.save()
