from django.urls import path

from .views import GHFDBExploreView, GHFDBMetaDataAPIView, GHFDBPathDownloadView

urlpatterns = [
    path("api/ghfdb/", GHFDBPathDownloadView.as_view(), name="ghfdb-api"),
    path("api/ghfdb/meta/", GHFDBMetaDataAPIView.as_view(), name="ghfdb-api-meta"),
    path("explore/", GHFDBExploreView.as_view(), name="ghfdb-explore"),
]
