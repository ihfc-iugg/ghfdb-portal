"""Assessment upload workflow routes (T011/T014/T019/T046/T047, plan.md
"The pages").

Three pages and three actions. The list is the way in, an assessment's own
page is where everything about one of them is reached, and uploading keeps
a page of its own because it carries a check report and a confirmation that
have nothing to do with describing an assessment.

The decision queue that lived at ``assessments/queue/`` is gone: it was the
list narrowed to one state, which the list's own filters now do.
"""

from django.urls import URLPattern, URLResolver, path

from .views import (
    ReviewConfirmView,
    ReviewCreateView,
    ReviewDecideView,
    ReviewDetailView,
    ReviewListView,
    ReviewUpdateView,
    ReviewUploadView,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path("assessments/", ReviewListView.as_view(), name="review-list"),
    path("assessments/new/", ReviewCreateView.as_view(), name="review-create"),
    path("assessments/<int:pk>/", ReviewDetailView.as_view(), name="review-detail"),
    path(
        "assessments/<int:pk>/edit/",
        ReviewUpdateView.as_view(),
        name="review-update",
    ),
    path(
        "assessments/<int:pk>/upload/",
        ReviewUploadView.as_view(),
        name="review-upload",
    ),
    path(
        "assessments/<int:pk>/confirm/",
        ReviewConfirmView.as_view(),
        name="review-confirm",
    ),
    path(
        "assessments/<int:pk>/decide/",
        ReviewDecideView.as_view(),
        name="review-decide",
    ),
]
