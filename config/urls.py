from django.urls import include, path

urlpatterns = [
    path("", include("review.urls")),
    path("", include("heat_flow.urls")),
    path("", include("fairdm.conf.urls")),
]
