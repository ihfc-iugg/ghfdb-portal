__license__ = 'MIT License <http://www.opensource.org/licenses/mit-license.php>'
__author__ = 'Lucas Theis <lucas@theis.io>'
__docformat__ = 'epytext'

try:
    from django.conf.urls import url
except ImportError:
    from django.conf.urls.defaults import url

from publications import views
from django.urls import path, include

app_name = 'publications'
urlpatterns = [
    # url(r'^$', views.year, name='index'),
    path('', views.year, name='index'),

    # url(r'^(?P<publication_id>\d+)/$', views.id, name='id'),
    path('<publication_id>',views.id, name='id'),
    # url(r'^year/(?P<year>\d+)/$', views.year, name='year'),
    path('year/<year>', views.year, name='year'),
    # url(r'^tag/(?P<keyword>.+)/$', views.keyword, name='keyword'),
    path('tag/<keyword>', views.keyword, name='keyword'),

    url(r'^list/(?P<list>.+)/$', views.list, name='list'),
    url(r'^unapi/$', views.unapi, name='unapi'),
    url(r'^(?P<name>.+)/$', views.author, name='author'),
]
