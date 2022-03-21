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
from api.v1.renderers import SiteDownloadRenderer
from rest_framework.settings import api_settings
from django.views import View
from django.views.decorators.cache import cache_page
from django.http import HttpResponse,  JsonResponse


class MapSites(APIView):

    def get(self, request, *args, **kwargs):
        filtered = MapFilter(request.GET, queryset=Site.objects.all())
        sites = filtered.qs.values_list('id','latitude','longitude',)
        return Response(list(sites))


class SiteViewSet(viewsets.ModelViewSet):
    """API endpoint to request a set of ThermoGlobe sites."""
    queryset = Site.objects.all()
    serializer_class = serialize.Site
    distance_filter_field = 'geom'
    distance_ordering_filter_field = 'geom'
    filterset_fields = ['reference',]
    filter_backends = (DistanceToPointFilter, DistanceToPointOrderingFilter,DjangoFilterBackend)


class PublicationViewSet(PaginateByMaxMixin, PublicationModelViewSet):
    """API endpoint to request a set of ThermoGlobe publications."""
    max_paginate_by = 1000
    serializer_class = serialize.PublicationSerializer
    filterset_fields = ['sites',]
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        return (super().get_queryset()
        .prefetch_related('sites','temperature_logs','heat_production_logs','conductivity_logs')
        )


class IntervalViewSet(viewsets.ModelViewSet):
    """API endpoint to request a set of heat flow intervals."""
    queryset = Interval.objects.select_related('site','reference')
    serializer_class = serialize.Interval
    filterset_fields = ['reference','site']
    filter_backends = (DjangoFilterBackend,)