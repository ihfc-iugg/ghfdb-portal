from django.urls import path, include
from thermoglobe import views
app_name = 'thermoglobe'

urlpatterns = [
    path('sites/',views.WorldMap.as_view(),name='world_map'),
    path('sites/<pk>/', views.SiteView.as_view(), name='site'), 
]
