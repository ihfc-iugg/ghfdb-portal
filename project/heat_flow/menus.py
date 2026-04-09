from django.utils.translation import gettext as _
from fairdm.menus import AppMenu
from flex_menu import MenuItem

AppMenu.insert(
    MenuItem(
        name=_("Explore"),
        view_name="ghfdb-explore",
    ),
    position=0,
)
