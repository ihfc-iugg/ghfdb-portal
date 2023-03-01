from django.urls import include, path
from api.v1 import views

# app_name = 'api'
urlpatterns = [
    path('sites/detail/<pk>/', views.MapPopupTemplate.as_view(),
         name='site_detail'),
]
