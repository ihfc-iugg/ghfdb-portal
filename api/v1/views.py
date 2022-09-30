from rest_framework import viewsets
from api.v1 import serialize
from database.models import Site, Interval
from rest_framework_gis.filters import DistanceToPointFilter
from api.utils import DistanceToPointOrderingFilter
from core.utils import DjangoFilterBackend
from main.filters import MapFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework_extensions.mixins import PaginateByMaxMixin
from rest_framework import generics
from rest_framework.renderers import TemplateHTMLRenderer
from django.contrib.gis.db.models.functions import AsGeoJSON
from time import time
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_orjson_renderer.renderers import ORJSONRenderer
from django.utils.html import mark_safe
from publications.models import Publication
from rest_access_policy.access_view_set_mixin import AccessViewSetMixin
from api.access_policies import SiteAccessPolicy
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from core.views import FieldSetMixin

class SiteViewSet(AccessViewSetMixin, viewsets.ModelViewSet):
    """API endpoint to request a set of ThermoGlobe sites."""
    access_policy = SiteAccessPolicy
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly,]
    queryset = Site.objects.all().prefetch_related('references')
    serializer_class = serialize.Site
    distance_filter_field = 'geom'
    distance_ordering_filter_field = 'geom'
    filterset_fields = ['references',]
    # filter_backends = (DistanceToPointFilter, DistanceToPointOrderingFilter, DjangoFilterBackend)
    filter_backends = (DistanceToPointFilter, DjangoFilterBackend)
    pagination_class = None


class FeatureList(generics.ListAPIView):
    queryset = Site.objects.all().annotate(geometry=AsGeoJSON('geom'))
    serializer_class = serialize.FeatureSerializer
    renderer_classes = [ORJSONRenderer]
    pagination_class = None
    filterset_fields = ['references',]
    # filter_backends = (DistanceToPointFilter, DistanceToPointOrderingFilter, DjangoFilterBackend)
    filter_backends = (DistanceToPointFilter, DjangoFilterBackend)

    def get_renderer_context(self):
        renderer_context = super().get_renderer_context()
        renderer_context["default_function"] = None
        return renderer_context


    @method_decorator(cache_page(60*60*24))
    def list(self, request, *args, **kwargs):
        start = time()
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        r = Response(serializer.data)
        print("GeoJSON took ", time()-start, 'seconds to load')

        return r


class PublicationViewSet(PaginateByMaxMixin, viewsets.ModelViewSet):
    """API endpoint to request a set of ThermoGlobe publications."""
    max_paginate_by = 1000
    serializer_class = serialize.PublicationSerializer
    filterset_fields = ['container_title', 'published']
    filter_backends = (DjangoFilterBackend,)
    queryset = Publication.objects.prefetch_related('sites','temperature_logs','heat_production_logs','conductivity_logs')

    def get_queryset(self):
        return (super().get_queryset())
        # .prefetch_related('sites','temperature_logs','heat_production_logs','conductivity_logs'))


class IntervalViewSet(viewsets.ModelViewSet):
    """API endpoint to request a set of heat flow intervals."""
    queryset = Interval.objects.select_related('site','reference')
    serializer_class = serialize.Interval
    filterset_fields = ['reference','site']
    filter_backends = (DjangoFilterBackend,)


class MapSites(APIView):
    schema=None

    def get(self, request, *args, **kwargs):

        filtered = MapFilter(request.GET, queryset=Site.objects.all())
        start = time()
        sites = filtered.qs.annotate(geometry=AsGeoJSON('geom'))
      

        features = [f'{{"id":"{f[0]}","type":"Feature","geometry":{f[1]},"properties":{{"q":{f[2]}}}}}' for f in sites.values_list('id','geometry','q')]

        json_str = '{"type":"FeatureCollection", "features":' + "[" + ",".join(features) + "]}"

        print("GeoJSON took ", time()-start, 'seconds to load')

        return HttpResponse(json_str, content_type="application/json")



# class MapSites(APIView):
#     schema=None

#     def get(self, request, *args, **kwargs):
#         filtered = MapFilter(request.GET, queryset=Site.objects.all())
#         start = time()

#         sites = filtered.qs.values_list('id','lat','lng',)
#         print("GeoJSON took ", time()-start, 'seconds to load')

#         return Response(list(sites))

class MapPopupTemplate(FieldSetMixin, generics.RetrieveAPIView):
    """
    A view that returns a templated HTML representation of a given site.
    """
    queryset = Site.objects.all()
    renderer_classes = [TemplateHTMLRenderer]
    schema=None
    fieldset = [
        (None, 
            {'fields': [
                'q',
                'q_unc',
                'method',
                'env',
                'expl',
                'wat_temp',
                'q_comment',
                ]}),
        # ('Geographic',
        #     {'fields': [ 
        #         'country',
        #         'political',
        #         'continent',
        #         'ocean',
        #         'province',
        #         'plate',
        #         ]}),
            ]

    def get(self, request, *args, **kwargs):
        context = dict(
            site = self.get_object(),
            fieldset = self.get_fieldset(),
        )
        return Response(context, template_name='api/map_popup.html')