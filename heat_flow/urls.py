from django.urls import path
from neapolitan.views import Role

from .views import GHFDBExploreView, GHFDBExport, GHFDBImport, GHFDBPathDownloadView, ReviewCRUDView

urlpatterns = [
    path("dataset/<str:pk>/ghfdb-import/", GHFDBImport.as_view(), name="ghfdb-import"),
    path("dataset/<str:pk>/ghfdb-export/", GHFDBExport.as_view(), name="ghfdb-export"),
    path("ghfdb/IHFC_2024_GHFDB.csv", GHFDBPathDownloadView.as_view(), name="ghfdb-download"),
    *ReviewCRUDView.get_urls(roles=[Role.CREATE, Role.UPDATE, Role.DELETE]),
    path("api/ghfdb/", GHFDBPathDownloadView.as_view(), name="ghfdb-api"),
    path("explore/", GHFDBExploreView.as_view(), name="ghfdb-explore"),
]
