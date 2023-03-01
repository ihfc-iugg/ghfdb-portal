from django.db.models import Count, Max, Min
from django.shortcuts import get_object_or_404
from geoluminate.utils.drf import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework_datatables_editor.viewsets import DatatablesEditorModelViewSet
from rest_pandas import PandasView

from .. import models
from . import serialize


class WellLogViewSet(DatatablesEditorModelViewSet):
    filterset_fields = ["reference", "site"]
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("site")
            .prefetch_related("data")
            .annotate(
                data_count=Count("data"),
                depth_upper=Min("data__depth"),
                depth_lower=Max("data__depth"),
            )
        )


class LogDataMixin(PandasView):
    serializer_class = serialize.TemperatureData
    model = models.TemperatureLog

    def get_queryset(self):
        return self.get_object().data.all()

    def get_object(self):
        return get_object_or_404(self.model, pk=self.kwargs.get("pk"))

    def get_pandas_filename(self, request, format):
        if format in ("xls", "xlsx"):
            # Use custom filename and Content-Disposition header
            # Extension will be appended automatically
            return str(self.get_object().pk)
        else:
            # Default filename from URL (no Content-Disposition header)
            return None

    def transform_dataframe(self, dataframe):
        dataframe.set_index("depth", inplace=True)
        return dataframe


class TemperatureViewSet(WellLogViewSet):
    """API endpoint to request temperature logs"""

    queryset = models.TemperatureLog.objects.all()
    serializer_class = serialize.TemperatureLogs


class TemperatureDataView(LogDataMixin):
    serializer_class = serialize.TemperatureData
    model = models.TemperatureLog


class ConductivityViewSet(WellLogViewSet):
    """API endpoint to request conductivity logs"""

    queryset = models.ConductivityLog.objects.all()
    serializer_class = serialize.ConductivityLogs


class ConductivityDataView(LogDataMixin):
    serializer_class = serialize.ConductivityData
    model = models.ConductivityLog
