from django.urls import path
from django.views.generic import TemplateView

from .views import GHFDBExploreView, GHFDBMetaDataAPIView, GHFDBPathDownloadView

urlpatterns = [
    path("api/ghfdb/", GHFDBPathDownloadView.as_view(), name="ghfdb-api"),
    path("api/ghfdb/meta/", GHFDBMetaDataAPIView.as_view(), name="ghfdb-api-meta"),
    path("explore/", GHFDBExploreView.as_view(), name="ghfdb-explore"),
    path("map/", TemplateView.as_view(template_name="fairdm/pages/home.html"), name="map"),
]
