from django.db import models
from django.db.models.functions import Coalesce

class IntervalManager(models.Manager):

    def __init__(self, field=None):
        super().__init__()
        if field:
            self.field = field

    def get_queryset(self):
        return (super().get_queryset()
        .annotate(
            heat_flow=Coalesce('heat_flow_corrected', 'heat_flow_uncorrected'),
            gradient=Coalesce('gradient_corrected', 'gradient_uncorrected'),)
        .exclude(**{f"{self.field}__isnull":True})
        )
 
