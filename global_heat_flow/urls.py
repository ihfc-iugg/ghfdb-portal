from cms.sitemaps import CMSSitemap
from django.contrib.gis import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.conf.urls.i18n import i18n_patterns

urlpatterns = i18n_patterns(
    path('', include('main.urls')),
    path('publications/', include('publications.urls')),
    path('datacite/', include('django_datacite.urls')),
    path('gfz-submit/', include('gfz_dataservices.urls')),
    path('', include('dashboard.urls')),
    path('earth_science', include('earth_science.urls')),
    path("invitations/", include('invitations.urls', namespace='invitations')),
    path('translate/', include('rosetta.urls')),
    path('admin/', include('smuggler.urls')),  # before admin url patterns!

    path('', include('core.urls')),
)

    
urlpatterns += [
    path("api/", include("api.urls")),
]


if settings.DEBUG:

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]


