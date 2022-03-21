
from rest_framework_datatables_editor.viewsets import DatatablesEditorModelViewSet
from .serialize import ConductivitySerializer, TemperatureSerializer, HeatProductionSerializer
from ..models import TemperatureLog, ConductivityLog, HeatProductionLog
from django.db.models import Count, Min, Max
from core.utils import DjangoFilterBackend


class WellLogViewSet(DatatablesEditorModelViewSet):
    """API endpoint to request a set of temperature measurements."""
    filterset_fields = ['reference','site']
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        return (super().get_queryset()
        .select_related('site')
        .prefetch_related('data')
        .annotate(
            data_count=Count('data'),
            depth_upper=Min('data__depth'),
            depth_lower=Max('data__depth'),
            )
        )


class TemperatureViewSet(WellLogViewSet):
    """API endpoint to request temperature logs"""
    queryset = TemperatureLog.objects.all()
    serializer_class = TemperatureSerializer



class ConductivityViewSet(WellLogViewSet):
    """API endpoint to request conductivity logs"""
    queryset = ConductivityLog.objects.all()
    serializer_class = ConductivitySerializer


class HeatProductionViewSet(WellLogViewSet):
    """API endpoint to request heat production logs"""
    queryset = HeatProductionLog.objects.all()
    serializer_class = HeatProductionSerializer
