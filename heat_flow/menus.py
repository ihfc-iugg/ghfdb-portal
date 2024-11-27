from django.utils.translation import gettext as _
from flex_menu import MenuItem
from geoluminate.menus import DatabaseMenu

DatabaseMenu.insert(
    [MenuItem(_("GHFDB"), view_name="map", icon="map")],
    position=4,
)
