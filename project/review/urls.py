"""Assessment upload workflow routes.

Empty for now: the routes the old Review record's views defined
(``review-list``, ``review-create``, ``community/reviewers/``) were retired
in the same phase that changed the record (T010a). The real routes for this
workflow are built in US-1 onward.
"""

from django.urls import URLPattern, URLResolver

urlpatterns: list[URLPattern | URLResolver] = []
