from django.utils.translation import gettext as _
from flex_menu import MenuItem
from geoluminate.menus import DatabaseMenu

DatabaseMenu.add_children(
    MenuItem(
        _("Map"),
        view_name="map",
        icon="map",
    )
)
