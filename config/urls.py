from django.urls import include, path

urlpatterns = [
    path("", include("review.urls")),
    path("", include("ghfdb.urls")),
    path("", include("fairdm.urls")),
]
