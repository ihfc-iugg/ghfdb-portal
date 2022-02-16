from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from api import serialize
from thermoglobe.models import Site, Interval, Conductivity, HeatProduction, Temperature
from publications.models import Publication
from api.paginators import DataTablesPaginator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework_gis.filters import DistanceToPointOrderingFilter, DistanceToPointFilter
# from rest_framework_gis.schema import GeoFeatureAutoSchema
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from thermoglobe.filters import MapFilter
from rest_framework_datatables_editor.viewsets import DatatablesEditorModelViewSet
from drf_renderer_xlsx.mixins import XLSXFileMixin
from drf_renderer_xlsx.renderers import XLSXRenderer


class GeoSiteViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to request a set of ThermoGlobe sites."""
    queryset = Site.objects.all()
    pagination_class = None
    serializer_class = serialize.GeoSite
    # filter_backends = (DistanceToPointFilter,DistanceToPointOrderingFilter,DjangoFilterBackend)
    filter_backends = (DistanceToPointFilter,DjangoFilterBackend,)
    # filterset_fields = ['site_name',]
    filterset_class = MapFilter

class SiteViewSet(XLSXFileMixin,DatatablesEditorModelViewSet):
    """API endpoint to request a set of ThermoGlobe sites."""
    queryset = Site.objects.all()
    serializer_class = serialize.Site
    distance_filter_field = 'geom'
    distance_ordering_filter_field = 'geom'
    filterset_fields = ['reference',]
    filter_backends = (DistanceToPointFilter, DistanceToPointOrderingFilter,DjangoFilterBackend)
    filename = 'my_export.xlsx'

class PublicationViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to request a set of ThermoGlobe publications."""
    queryset = Publication.objects.all()
    serializer_class = serialize.Publication

class HeatFlowViewSet(DatatablesEditorModelViewSet):
    """API endpoint to request a set of heat flow intervals."""
    queryset = Interval.heat_flow.select_related('site','reference')
    serializer_class = serialize.Interval
    filterset_fields = ['reference','site']

class GradientViewSet(DatatablesEditorModelViewSet):
    """API endpoint to request a set of thermal gradient intervals."""
    queryset = Interval.gradient.all()
    serializer_class = serialize.Interval
    filterset_fields = ['reference','site']

class ConductivityViewSet(XLSXFileMixin,DatatablesEditorModelViewSet):
    """API endpoint to request a set of thermal conductivity measurements."""
    queryset = Conductivity.objects.select_related('reference','site')
    serializer_class = serialize.Conductivity
    filterset_fields = ['site','reference']
    filename = 'my_export.xlsx'

class HeatProductionViewSet(DatatablesEditorModelViewSet):
    """API endpoint to request a set of heat production measurements."""
    queryset = HeatProduction.objects.all()
    serializer_class = serialize.HeatProduction
    filterset_fields = ['reference','site']

class TemperatureViewSet(DatatablesEditorModelViewSet):
    """API endpoint to request a set of temperature measurements."""
    queryset = Temperature.objects.all()
    serializer_class = serialize.Temperature
    filterset_fields = ['reference','site']