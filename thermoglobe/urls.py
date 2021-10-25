from django.urls import path, include
from thermoglobe import views
# app_name = 'thermoglobe'


urlpatterns = [
    path('world-map/',views.WorldMap.as_view(),name='world_map'),
    path('sites/<slug>/', views.SiteView.as_view(), name='site'),
    path('publications/', views.PublicationListView.as_view(),name='publication_list'),
    path('publications/<slug>/',views.PublicationDetailsView.as_view(),name='publication_details'),
]
