from enum import unique
from rest_framework import viewsets
from api.v1 import serialize
from thermoglobe.models import Site, Interval
from publications.models import Publication
from rest_framework_gis.filters import DistanceToPointOrderingFilter, DistanceToPointFilter
from rest_framework_datatables_editor.viewsets import DatatablesEditorModelViewSet
from core.utils import DjangoFilterBackend
from thermoglobe.filters import MapFilter
from rest_framework.views import APIView
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework.response import Response
from rest_framework_extensions.mixins import PaginateByMaxMixin
from django.db.models import Count, Min, Max
from publications.api.views import PublicationModelViewSet
from rest_framework_csv.renderers import PaginatedCSVRenderer
from rest_framework_csv.renderers import CSVRenderer
from rest_framework.settings import api_settings
from rest_framework.generics import ListAPIView

class MapSites(APIView):

    @cache_response()
    def get(self, request, *args, **kwargs):
        filtered = MapFilter(request.GET, queryset=Site.objects.all())
        sites = filtered.qs.values_list('id','latitude','longitude',)
        return Response(sites)


class SiteDownloadView(ListAPIView):
    """API endpoint to request a set of ThermoGlobe sites."""
    queryset = Site.objects.all()[:1000]
    serializer_class = serialize.Site
    renderer_classes = (CSVRenderer,)  + tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    pagination_class = None

    # def get(self, request, *args, **kwargs):
    #     filtered = MapFilter(request.GET, queryset=Site.objects.all())
    #     sites = filtered.qs.values_list('id','latitude','longitude',)
    #     return Response(sites)
