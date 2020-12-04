from django.urls import path, include
from thermoglobe import views
app_name = 'thermoglobe'

urlpatterns = [
    path('thermoglobe/', 
        include([
            path('worldmap/',views.WorldMap.as_view(),name='world_map'),
            path('sites/<slug>/', views.SiteView.as_view(), name='site'),
            path('upload/',views.UploadView.as_view(),name='upload'),
            path('upload/confirm', views.upload_confirm, name='confirm_upload'),
            path('upload_template/<template_name>', views.get_upload_template, name='template'),
            path('publications/', include([
                    path('', views.PublicationListView.as_view(),name='publication_list'),
                    path('<slug>/',views.PublicationDetailsView.as_view(),name='publication_details'),
                    ])
                ),
            path('authors/', include([
                    path('<slug>/',views.AuthorDetailsView.as_view(),name='author_details'),
                    ])
                ),
        ])),
    path('', 
        include([
            path('heat-flow/', views.ExploreHeatFlow.as_view(), name='heat_flow'),
            path('thermal-gradient/', views.ExploreGradient.as_view(), name='gradient'),
            # path('conductivity/', views.ExploreConductivity.as_view(), name='conductivity'),
            # path('temperature/', views.ExploreTemperature.as_view(), name='temperature'),
            # path('heat-generation/', views.ExploreHeatGen.as_view(), name='heat_gen'),
        ])),
]
