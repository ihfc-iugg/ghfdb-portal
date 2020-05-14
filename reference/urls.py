from django.urls import path, include
from . import views
app_name = 'reference'

urlpatterns = [
    path('thermoglobe/publications/', include([
            path('',views.PublicationListView.as_view(),name='publication_list'),
            path('<slug>/',views.PublicationDetailsView.as_view(),name='publication_details'),
            path('<slug>/data.json',views.publication_data,name='publication_data'),
            ])
        ),
    path('thermoglobe/authors/', include([
            path('',views.AuthorListView.as_view(),name='author_list'),
            path('<slug>/',views.AuthorDetailsView.as_view(),name='author_details'),
            ])
        ),

    ]
