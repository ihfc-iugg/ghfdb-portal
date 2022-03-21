from django.db import models
from django.db.models.functions import Coalesce
from core.querysets import QuerySetExtra

class IntervalQueryset(QuerySetExtra):

    def heat_flow(self):
        return self.exclude(heat_flow__isnull=True)

    def gradient(self):
        return self.exclude(gradient__isnull=True)




class IntervalManager(models.Manager):

    def __init__(self, field=None):
        super().__init__()
        if field:
            self.field = field

    def get_queryset(self):
        return IntervalQueryset(self.model, using=self._db).annotate(
            heat_flow=Coalesce('heat_flow_corrected', 'heat_flow_uncorrected'),
            heat_flow_uncertainty=Coalesce('heat_flow_corrected_uncertainty', 'heat_flow_uncorrected_uncertainty'),
            gradient=Coalesce('gradient_corrected', 'gradient_uncorrected'),
            gradient_uncertainty=Coalesce('gradient_corrected_uncertainty', 'gradient_uncorrected_uncertainty'),)

    def heat_flow(self):
        return self.get_queryset().heat_flow()

    def gradient(self):
        return self.get_queryset().gradient()