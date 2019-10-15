from django.urls import path
from . import views
app_name = 'mapping'

urlpatterns = [

    path('thermoglobe/map',views.FullMapView.as_view(),name='thermoglobe'),
    path('thermoglobe/filter', views.filter_data,name='filter_data'),



]
