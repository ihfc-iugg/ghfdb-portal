from django.urls import include, path
from rest_framework import routers
from api import views
from rest_framework.schemas import get_schema_view
from rest_framework_gis.schema import GeoFeatureAutoSchema

router = routers.DefaultRouter()
router.register(r'site', views.SiteViewSet)
router.register(r'publication', views.PublicationViewSet)
router.register(r'heat-flow', views.HeatFlowViewSet,basename='heat-flow')
router.register(r'gradient', views.GradientViewSet)
router.register(r'conductivity', views.ConductivityViewSet)
router.register(r'heat-production', views.HeatProductionViewSet)
router.register(r'temperature', views.TemperatureViewSet)

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