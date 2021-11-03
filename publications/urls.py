from django.conf.urls import url
from publications import views
from django.urls import path

app_name = 'publications'
urlpatterns = [
    path('', views.year, name='index'),
    path('year/<year>', views.year, name='year'),
    path('<publication_id>',views.id, name='id'),
    path('tag/<keyword>', views.keyword, name='keyword'),
    url(r'^(?P<name>.+)/$', views.author, name='author'),
]
