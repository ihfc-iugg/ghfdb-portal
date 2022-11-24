"""
Contains the project wide url patterns used in the application.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/http/urls/
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.shortcuts import redirect

urlpatterns = [
    path("api/", include("geoluminate.api.urls")),
]

urlpatterns += i18n_patterns(
    # path('datacite/', include('datacite.urls')),
    path('earth_science', include('earth_science.urls')),
    path("invitations/", include('invitations.urls', namespace='invitations')),
    path('admin/', include('smuggler.urls')),
    path('datatables/', include('datatables.urls')),
    path('literature/review-project/', include('review.urls')),
    path('api/', lambda request: redirect('swagger-ui', permanent=False)),
    path('', include('geoluminate.urls')),
)


if settings.DEBUG:

    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
