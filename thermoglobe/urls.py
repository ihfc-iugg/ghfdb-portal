from django.urls import path, include
from thermoglobe.views import About, SiteView, UploadView, WorldMap, data
app_name = 'thermoglobe'

urlpatterns = [
    path('thermoglobe/', 
        include([
            path('',About.as_view(), name='about'),
            path('worldmap/',WorldMap.as_view(),name='world_map'),
            path('data/', data, name='data'),
            path('sites/<slug>/', SiteView.as_view(), name='site'),
            path('upload/',UploadView.as_view(),name='upload'),
        ])),
]
