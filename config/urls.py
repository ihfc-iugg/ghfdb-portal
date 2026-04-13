from django.urls import include, path

urlpatterns = [
    path("ghfdb/", include("project.ghfdb.urls")),
    path("", include("review.urls")),
    path("", include("heat_flow.urls")),
    path("", include("fairdm.conf.urls")),
]
