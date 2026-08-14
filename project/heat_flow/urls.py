from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path(
        "map/", TemplateView.as_view(template_name="fairdm/pages/home.html"), name="map"
    ),
]
