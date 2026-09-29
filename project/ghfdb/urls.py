"""URL routes for the GHFDB app.

Also registers the published-structure viewsets on the framework's own API
router. That registration must run before ``fairdm.api.urls`` is imported —
`config/urls.py` includes this module ahead of ``fairdm.conf.urls``, which is
what makes the ordering here work (research R1).
"""

from django.urls import path
from fairdm.api.router import fairdm_api_router

from .views import GHFDBExploreView, GHFDBMetaDataAPIView, GHFDBPathDownloadView
from .viewsets import GHFDBChildViewSet, GHFDBParentViewSet

fairdm_api_router.register(
    r"ghfdb/parents", GHFDBParentViewSet, basename="ghfdb-parents"
)
fairdm_api_router.register(
    r"ghfdb/children", GHFDBChildViewSet, basename="ghfdb-children"
)

urlpatterns = [
    path("api/ghfdb/", GHFDBPathDownloadView.as_view(), name="ghfdb-api"),
    path("api/ghfdb/meta/", GHFDBMetaDataAPIView.as_view(), name="ghfdb-api-meta"),
    path("explore/", GHFDBExploreView.as_view(), name="ghfdb-explore"),
]
