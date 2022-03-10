from django.urls import include, path
from rest_framework import routers
from api import views
from rest_framework.schemas import get_schema_view
from rest_framework_gis.schema import GeoFeatureAutoSchema
from well_logs.api.views import TemperatureViewSet, ConductivityViewSet, HeatProductionViewSet
router = routers.DefaultRouter()
# router.register(r'geojson/site', views.GeoSiteViewSet,basename='geojson')
router.register(r'sites', views.SiteViewSet)
router.register(r'publications', views.PublicationViewSet)
router.register(r'intervals/heat-flow', views.HeatFlowViewSet,basename='heat-flow')
router.register(r'intervals/gradient', views.GradientViewSet)
router.register(r'logs/conductivity', ConductivityViewSet)
router.register(r'logs/heat-production', HeatProductionViewSet)
router.register(r'logs/temperature', TemperatureViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # path('nearest-sites/', views.SiteRetrieveView.as_view()),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('openapi/', get_schema_view(
        title="ThermoGlobe",
        description="API for ThermoGlobe database",
        version="beta",
    ), name='openapi-schema'),
]