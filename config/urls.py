from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("", include("heat_flow.urls")),
    path("", include("fairdm.urls")),
    path("map/", TemplateView.as_view(template_name="fairdm/pages/home.html"), name="map"),
]
