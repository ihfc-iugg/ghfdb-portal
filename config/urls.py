from django.urls import include, path

urlpatterns = [
    path("", include("geoluminate.urls")),
    path("", include("earth_science.location.urls")),
]
