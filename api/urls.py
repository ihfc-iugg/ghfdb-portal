from django.urls import include, path
from django.shortcuts import redirect

urlpatterns = [
    path('v1/', include("api.v1.urls")),
    path('', lambda request: redirect('/api/v1', permanent=False))
]