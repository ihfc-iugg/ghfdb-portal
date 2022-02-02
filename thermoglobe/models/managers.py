from django.db import models
from django.db.models.functions import Coalesce

class IntervalManager(models.Manager):

    def __init__(self, field=None):
        super().__init__()
        if field:
            self.field = field

    def get_queryset(self):
        return super().get_queryset().annotate(
            heat_flow=Coalesce('heat_flow_corrected', 'heat_flow_uncorrected'),
            heat_flow_uncertainty=Coalesce('heat_flow_corrected_uncertainty', 'heat_flow_uncorrected_uncertainty'),
            gradient=Coalesce('gradient_corrected', 'gradient_uncorrected'),
            gradient_uncertainty=Coalesce('gradient_corrected_uncertainty', 'gradient_uncorrected_uncertainty'),)

class HeatFlowManager(IntervalManager):

    def get_queryset(self):
        return super().get_queryset().exclude(heat_flow__isnull=True)
 
class GradientManager(IntervalManager):

    def get_queryset(self):
        return super().get_queryset().exclude(gradient__isnull=True)