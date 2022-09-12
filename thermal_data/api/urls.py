from django.urls import include, path
from rest_framework import routers
from well_logs.api import views

router = routers.DefaultRouter()

router.register(r'conductivity-log', views.ConductivityViewSet)
router.register(r'temperature-log', views.TemperatureViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('temperature-log/<pk>/data/', views.TemperatureDataView.as_view()),
    path('conductivity-log/<pk>/data/', views.ConductivityDataView.as_view()),
]