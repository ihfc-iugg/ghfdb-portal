from django.urls import include, path
from geoluminate.contrib.project.api.viewsets import MeasurementViewset
from rest_framework_nested import routers

from .models import HeatFlow, Interval

router = routers.SimpleRouter()
router.register(r"heat-flow", MeasurementViewset(model=HeatFlow), basename="heat-flow")


heat_flow = routers.NestedSimpleRouter(router, r"heat-flow", lookup="heat_flow")
heat_flow.register(r"intervals", MeasurementViewset(model=Interval))

urlpatterns = [
    path("measurements/", include(router.urls)),
    path("measurements/", include(heat_flow.urls)),
]
