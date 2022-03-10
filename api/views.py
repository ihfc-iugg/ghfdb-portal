from rest_framework import viewsets
from api import serialize
from thermoglobe.models import Site, Interval
from publications.models import Publication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_gis.filters import DistanceToPointOrderingFilter, DistanceToPointFilter
from thermoglobe.filters import MapFilter
from rest_framework_datatables_editor.viewsets import DatatablesEditorModelViewSet
from drf_excel.mixins import XLSXFileMixin


class DisabledFilterBackend(DjangoFilterBackend):

    def to_html(self, request, queryset, view):
        return ""


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
    filter_backends = (DistanceToPointFilter, DistanceToPointOrderingFilter,DisabledFilterBackend)
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
    filter_backends = (DisabledFilterBackend,)


class GradientViewSet(DatatablesEditorModelViewSet):
    """API endpoint to request a set of thermal gradient intervals."""
    queryset = Interval.gradient.all()
    serializer_class = serialize.Interval
    filterset_fields = ['reference','site']
