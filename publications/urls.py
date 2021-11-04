from django.conf.urls import url
from publications import views
from django.urls import path

app_name = 'publications'
urlpatterns = [
    path('',views.PublicationListView.as_view(),name='list'),
    path('<pk>',views.PublicationDetailsView.as_view(),name='detail'),
]
