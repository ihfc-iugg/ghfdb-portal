from django.urls import path, include
from thermoglobe.views import (
    SiteView, UploadView, WorldMap, ExploreHeatFlow,ExploreHeatGen,ExploreConductivity, ExploreTemperature, ExploreGradient, data, get_upload_template, plots)
app_name = 'thermoglobe'

urlpatterns = [
    path('thermoglobe/', 
        include([
            path('worldmap/',WorldMap.as_view(),name='world_map'),
            path('data/', data, name='data'),
            path('heatflow/', ExploreHeatFlow.as_view(), name='heat_flow'),
            path('thermalgradient/', ExploreGradient.as_view(), name='gradient'),
            path('conductivity/', ExploreConductivity.as_view(), name='conductivity'),
            path('temperature/', ExploreTemperature.as_view(), name='temperature'),
            path('heat-generation/', ExploreHeatGen.as_view(), name='heat_gen'),
            path('sites/<slug>/', SiteView.as_view(), name='site'),
            path('upload/',UploadView.as_view(),name='upload'),
            path('upload_template/<template_name>', get_upload_template, name='template'),
            path('plots/',plots,name='plots'),
        ])),
]
