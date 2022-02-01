from cms.sitemaps import CMSSitemap
from django.contrib.gis import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns



urlpatterns = i18n_patterns(
    path("sitemap.xml", sitemap, {"sitemaps": {"cmspages": CMSSitemap}}),
    path("accounts/", include("allauth.urls")),
    path('', include('users.urls')),

    path('taggit_autosuggest/', include('taggit_autosuggest.urls')),
    path('', include('thermoglobe.urls')),
    path('publications/', include('publications.urls')),
    path('comments/', include('django_comments.urls')),
    path('', include('dashboard.urls')),

    path('grappelli/', include('grappelli.urls')), # grappelli URLS
    path("admin/", admin.site.urls), 
    path('', include("cms.urls")),
    
)

    
urlpatterns += [
    path("api/", include("api.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



