from django.urls import resolve, reverse

from heat_flow.models import HeatFlow, HeatFlowChild

# def test_detail(user: User):
#     assert (
#         reverse("users:detail", kwargs={"username": users.Username})
#         == f"/users/{users.Username}/"
#     )
#     assert resolve(f"/users/{users.Username}/").view_name == "users:detail"


# def test_update():
#     assert reverse("users:update") == "/users/~update/"
#     assert resolve("/users/~update/").view_name == "users:update"


# def test_redirect():
#     assert reverse("users:redirect") == "/users/~redirect/"
#     assert resolve("/users/~redirect/").view_name == "users:redirect"
