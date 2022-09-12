from django.urls import path, include
from main import views
app_name = 'main'

urlpatterns = [
    path('sites/',views.WorldMap.as_view(),name='world_map'),
    path('sites/<pk>/', views.SiteView.as_view(), name='site'), 
]
