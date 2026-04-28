from django.utils.translation import gettext as _
from fairdm.menus import AppMenu
from flex_menu import MenuItem

AppMenu.insert(
    MenuItem(
        name=_("Explore"),
        view_name="ghfdb-explore",
        extra_context={"icon": "map"},
    ),
    position=0,
)
#     MenuItem(
#     name=_("Datasets"),
#     view_name="dataset-list",
#     extra_context={
#         "icon": "dataset",
#     },
# ),
