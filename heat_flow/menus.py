from django.utils.translation import gettext as _
from flex_menu import MenuItem
from geoluminate.menus import DatabaseMenu

DatabaseMenu.insert(
    [
        MenuItem(_("Global Heat Flow Database"), view_name="map", icon="map"),
    ],
    position=0,
)

DatabaseMenu.insert(
    [
        MenuItem(_("International Heat Flow Commission"), url="https://ihfc-iugg.org", icon="globe"),
        MenuItem(_("Portal Team"), view_name="home", icon="contributors"),
    ],
    position=6,
)


# DatabaseMenu.ge
