from django.urls import path
from . import views
app_name = 'mapping'

urlpatterns = [

    path('thermoglobe/map',views.FullMapView.as_view(),name='thermoglobe'),
    path('thermoglobe/data', views.data,name='data'),



]
