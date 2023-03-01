from geoluminate.utils.import_export import ResourceMixin

from .models import Conductivity, Temperature


class LogMixin(ResourceMixin):
    class Meta:
        exclude = ["date_added", "id"]
        import_id_fields = ["depth", "value"]
        # skip_diff = True
        # force_init_instance = True


class TempResource(LogMixin):
    class Meta:
        model = Temperature


class ConductivityResource(LogMixin):
    class Meta:
        model = Conductivity

    def before_import_row(self, row, row_number=None, **kwargs):
        return super().before_import_row(row, row_number, **kwargs)
