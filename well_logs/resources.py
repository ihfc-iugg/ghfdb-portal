from .models import ConductivityLog, HeatProductionLog, TemperatureLog
from .models import Conductivity, HeatProduction, Temperature, Sample
from import_export import resources
from django.utils.html import mark_safe
from tqdm import tqdm
from core.resources import ResourceMixin


class LogMixin(ResourceMixin):

    class Meta:
        exclude = ['date_added']
        import_id_fields = ['id']
        skip_diff=True
        force_init_instance = True

class TempResource(LogMixin):
    class Meta:
        model = Temperature

class HeatProductionResource(LogMixin):
    class Meta:
        model = HeatProduction

class ConductivityResource(LogMixin):
    class Meta:
        model = Conductivity

    def before_import_row(self, row, row_number=None, **kwargs):

        values = {k:row.get(k) for k in ['rock_type','length','width','diameter','thickness'] if row.get(k)}

        s = Sample.objects.create(**values)

        row['sample'] = s.id
      
        return super().before_import_row(row, row_number, **kwargs)