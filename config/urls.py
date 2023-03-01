"""
Contains project wide url patterns used in the application. You should
only need to modify this file if you are adding or removing
additional Django applications.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/http/urls/
"""
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.urls import include, path
from django.views import defaults as default_views

# API urls need to remain outside the i18n patterns
NON_I18N_URLS = [
    path("api/", include("geoluminate.contrib.api.urls")),
]

urlpatterns = (
    NON_I18N_URLS
    # i18n patterns will adapt their language to the end user if translations exist
    + i18n_patterns(
        path("geoscience", include("geoscience.urls")),
        path("literature/review-project/", include("review.urls")),
        # add any other i18n patterns ABOVE this line
        path("", include("geoluminate.urls")),
    )
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]

    # adds the debug toolbar to templates if installed
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
