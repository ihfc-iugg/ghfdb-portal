from django.urls import path

from review import views

# from .menu import ReviewMenu
app_name = "review"
urlpatterns = [
    # path("", views.ReviewDataTable.as_view(), name="review_list"),
    # path("", views.ReviewList.as_view(), name="list"),
    # path("register/", views.BecomeReviewer.as_view(), name="become_a_reviewer"),
    path("<pk>/", views.ReviewDetailView.as_view(), name="review_detail"),
    path("<pk>/edit", views.EditView.as_view(), name="edit"),
    # path("<pk>/submit", views.submit, name="submit"),
    # path("<pk>/accept", views.accept_review, name="accept"),
    # path("<pk>/nominate/", views.nominate_to_review_publication, name="nominate"),
    # path('<pk>/', include(ReviewMenu().get_url_patterns())),
    # path('', views.user_review, name='user_review'),
]
