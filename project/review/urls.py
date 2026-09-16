"""Assessment upload workflow routes (T011/T014/T019, plan.md "The pages").

The routes the old Review record's views defined (``review-list``,
``review-create``, ``community/reviewers/``) were retired in the same phase
that changed the record (T010a). ``review-list`` and ``review-create`` are
restored here, at the paths plan.md's access table gives them; the rest of
the table's routes are built from US-3 onward.
"""

from django.urls import URLPattern, URLResolver, path

from .views import (
    ReviewConfirmView,
    ReviewCreateView,
    ReviewListView,
    ReviewQueueView,
    ReviewUploadView,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path("assessments/", ReviewListView.as_view(), name="review-list"),
    path("assessments/new/", ReviewCreateView.as_view(), name="review-create"),
    path("assessments/queue/", ReviewQueueView.as_view(), name="review-queue"),
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
]
