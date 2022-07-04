from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class RangeField(models.FloatField):

    def __init__(self, range_min, range_max, *args, **kwargs):
        validators = kwargs.pop('validators')
        validators = [  MaxValueValidator(range_max),
                        MinValueValidator(range_min)],
        super().__init__(validators=validators,*args, **kwargs)