"""Assessment upload workflow routes (T011/T014, plan.md "The pages").

The routes the old Review record's views defined (``review-list``,
``review-create``, ``community/reviewers/``) were retired in the same phase
that changed the record (T010a). ``review-list`` is restored here, at the
path plan.md's access table gives it; the rest of the table's routes are
built from US-2 onward.
"""

from django.urls import URLPattern, URLResolver, path

from .views import ReviewListView

urlpatterns: list[URLPattern | URLResolver] = [
    path("assessments/", ReviewListView.as_view(), name="review-list"),
]
