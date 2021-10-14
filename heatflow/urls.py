from cms.sitemaps import CMSSitemap
from django.contrib.gis import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("sitemap.xml", sitemap, {"sitemaps": {"cmspages": CMSSitemap}}),
    path('taggit_autosuggest/', include('taggit_autosuggest.urls')),
]

urlpatterns += i18n_patterns(path("admin/", admin.site.urls), path("", include("cms.urls")))

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



