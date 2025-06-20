from django.urls import path

from .views import ReviewCreateView, ReviewListView

urlpatterns = [
    path("reviews/", ReviewListView.as_view(), name="review-list"),
    path("reviews/<int:literature_id>/create/", ReviewCreateView.as_view(), name="review-create"),
    # path("dataset/<int:literature_id>/create/", ReviewCreateView.as_view(), name="review-create"),
]
