"""
A collection of functions that hook into Django's model signals.

For more information on signals, see
https://docs.djangoproject.com/en/3.2/topics/signals/
"""

from django.db.models.signals import m2m_changed, post_save, pre_save
from django.dispatch import receiver
from ghfdb.models import Interval


@receiver(post_save, sender=Interval)
def interval_changed(sender, instance, **kwargs):
    """Ensures that every time a `ghfdb.models.Interval`instance
    is saved, the associated reference will also be saved on the associated
    `ghfdb.models.HeatFlow`.

    Args:
        sender (_type_): ghfdb.models.Interval
        instance (_type_): ghfdb.models.Interval
    """
    # Preliminary test to update Site instance after modifying an Interval

    # Current updates the site acquisition date to the latest acquired
    # Interval and adds the interval reference to the site object
    site = instance.site
    # most_recent = site.intervals.order_by('-q_date_acq').first()

    # site.q_date_acq = most_recent.q_date_acq
    site.references.add(instance.reference)
    site.save()
