from django.urls import include, path
from rest_framework import routers
from api import views

router = routers.DefaultRouter()
router.register(r'site', views.SiteViewSet)
router.register(r'publication', views.PublicationViewSet)
router.register(r'heat-flow', views.HeatFlowViewSet,basename='heat-flow')
router.register(r'gradient', views.GradientViewSet)
router.register(r'conductivity', views.ConductivityViewSet)
router.register(r'heat-production', views.HeatProductionViewSet)
router.register(r'temperature', views.TemperatureViewSet)

# app_label = 'api'
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]