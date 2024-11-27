from django.urls import path
from neapolitan.views import Role

from .views import GHFDBPathDownloadView, GHFDBUpload, ReviewCRUDView

urlpatterns = [
    path("dataset/<str:pk>/upload/", GHFDBUpload.as_view(), name="dataset-upload"),
    path("ghfdb/IHFC_2024_GHFDB.csv", GHFDBPathDownloadView.as_view(), name="ghfdb-download"),
    *ReviewCRUDView.get_urls(roles=[Role.CREATE, Role.UPDATE, Role.DELETE]),
    path("api/ghfdb/", GHFDBPathDownloadView.as_view(), name="ghfdb-api"),
]
