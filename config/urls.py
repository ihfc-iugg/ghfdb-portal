from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("", include("geoluminate.urls")),
    path("", include("earth_science.location.urls")),
    path("map/", TemplateView.as_view(template_name="home.html"), name="map"),
]
