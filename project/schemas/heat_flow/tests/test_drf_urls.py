from django.urls import resolve, reverse

from heat_flow.models import HeatFlow

# def test_user_detail(user: User):
#     assert (
#         reverse("api:user-detail", kwargs={"username": users.Username})
#         == f"/api/users/{users.Username}/"
#     )
#     assert resolve(f"/api/users/{users.Username}/").view_name == "api:user-detail"


# def test_user_list():
#     assert reverse("api:user-list") == "/api/users/"
#     assert resolve("/api/users/").view_name == "api:user-list"


# def test_user_me():
#     assert reverse("api:user-me") == "/api/users/me/"
#     assert resolve("/api/users/me/").view_name == "api:user-me"
