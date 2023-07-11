from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from geoluminate.menus import GeoluminateMenuBase, Sidebar
from simple_menu import MenuItem

# add a menu item to the sidebar that allow users to view datasets that are in review
Sidebar.add_item(
    MenuItem(
        title=_("Review"),
        url=reverse("review:ReviewDataTable:view"),
        weight=8,
        icon="fa-pencil-ruler",
    ),
)


class AppMenu(GeoluminateMenuBase):
    menu_name = "review_app_menu"


AppMenu.add_items(
    MenuItem(
        title=_("Description"),
        url=lambda r: reverse("review:edit", args=[r.resolver_match.kwargs.get("pk")]),
        weight=1,
        icon="fa-circle-info",
    ),
    MenuItem(
        title=_("Publications"),
        url=lambda r: reverse("review:edit", args=[r.resolver_match.kwargs.get("pk")]),
        weight=1,
        icon="fa-book",
    ),
    MenuItem(
        title=_("Contributors"),
        url=lambda r: reverse("review:edit", args=[r.resolver_match.kwargs.get("pk")]),
        weight=1,
        icon="fa-users",
    ),
    MenuItem(
        title=_("Data"),
        url=lambda r: reverse("review:edit", args=[r.resolver_match.kwargs.get("pk")]),
        weight=1,
        icon="fa-table",
    ),
    MenuItem(
        title=_("Map"),
        url=lambda r: reverse("review:edit", args=[r.resolver_match.kwargs.get("pk")]),
        weight=1,
        icon="fa-map-marked-alt",
    ),
)
