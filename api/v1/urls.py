from django.urls import include, path
from rest_framework import routers
from api.v1 import views
from rest_framework.schemas import get_schema_view
from rest_framework_gis.schema import GeoFeatureAutoSchema
from well_logs.api.views import TemperatureViewSet, ConductivityViewSet, HeatProductionViewSet
from api.v1.views import MapSites
from api.v1.download_views import SiteDownloadView

router = routers.DefaultRouter()

router.register(r'sites', views.SiteViewSet, basename='site')
router.register(r'publications', views.PublicationViewSet, basename='publication')
router.register(r'interval', views.IntervalViewSet)
router.register(r'conductivity', ConductivityViewSet)
router.register(r'heat-production', HeatProductionViewSet)
router.register(r'temperature', TemperatureViewSet)

urlpatterns = [
    path('sites/coordinates/', MapSites.as_view(), name='quick_sites'),
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('openapi/', get_schema_view(
        title="ThermoGlobe",
        description="API for ThermoGlobe database",
        version="beta",
    ), name='openapi-schema'),
]