from django.urls import include, path
from rest_framework import routers
from api.v1 import views
from rest_framework.schemas import get_schema_view
from rest_framework_gis.schema import GeoFeatureAutoSchema
# from well_logs.api.views import TemperatureViewSet, ConductivityViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

router = routers.DefaultRouter()
router.register(r'sites', views.SiteViewSet, basename='site')
router.register(r'intervals', views.IntervalViewSet)
router.register(r'publications', views.PublicationViewSet, basename='publication')


urlpatterns = [
    path('sites/coordinates/', views.MapSites.as_view(), name='quick_sites'),
    path('sites/detail/<pk>/', views.MapPopupTemplate.as_view(), name='site_detail'),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('', include(router.urls)),
    path('', include("thermal_data.api.urls")),

    path('geofeatures/', views.FeatureList.as_view()),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
]