from django.urls import path
from . import views
app_name = 'mapping'

urlpatterns = [

    path('thermoglobe/',views.FullMapView.as_view(),name='thermoglobe'),
    path('thermoglobe/filter', views.filter_data,name='filter_data'),



]
