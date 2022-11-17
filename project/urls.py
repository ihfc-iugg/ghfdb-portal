from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = i18n_patterns(
    path('datacite/', include('datacite.urls')),
    path('earth_science', include('earth_science.urls')),
    path("invitations/", include('invitations.urls', namespace='invitations')),
    path('admin/', include('smuggler.urls')),
    path('datatables/', include('datatables.urls')),
    path('literature/', include('review.urls')),
    path('', include('geoluminate.urls')),
)


urlpatterns += [
    path("api/", include("geoluminate.api.urls")),
]


if settings.DEBUG:

    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
