from cms.sitemaps import CMSSitemap
from django.contrib.gis import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.conf.urls import url




urlpatterns = [
    path("sitemap.xml", sitemap, {"sitemaps": {"cmspages": CMSSitemap}}),
    path('taggit_autosuggest/', include('taggit_autosuggest.urls')),
    path("admin/", admin.site.urls), 
    path('', include('thermoglobe.urls')),
    path('publications/', include('publications.urls')),
    path("api/", include("api.urls")),
    path("", include("cms.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



