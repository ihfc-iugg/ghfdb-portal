# from .models import Conductivity, Temperature
from geoluminate.resources import ResourceMixin


class LogMixin(ResourceMixin):

    class Meta:
        exclude = ['date_added', 'id']
        import_id_fields = ['depth', 'value']
        skip_diff = True
        force_init_instance = True


class TempResource(LogMixin):
    class Meta:
        # model = Temperature
        pass


class ConductivityResource(LogMixin):
    class Meta:
        # model = Conductivity
        pass

    def before_import_row(self, row, row_number=None, **kwargs):
        return super().before_import_row(row, row_number, **kwargs)
