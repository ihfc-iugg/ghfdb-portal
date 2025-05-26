from django.utils.translation import gettext as _
from fairdm.menus import DatabaseMenu
from flex_menu import MenuItem

DatabaseMenu.insert(
    [
        MenuItem(
            _("Explore"),
            view_name="ghfdb-explore",
            icon="map",
        ),
    ],
    position=1,
)
