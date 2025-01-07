from django.utils.translation import gettext as _
from flex_menu import Menu, MenuItem
from geoluminate.menus import DatabaseMenu

DatabaseMenu.insert(
    [
        Menu(
            "MapMenu",
            template="geoluminate/menus/database/menu.html",
            label=None,
            children=[
                MenuItem(_("Global Heat Flow Database"), view_name="map", icon="map"),
            ],
        ),
    ],
    position=0,
)


DatabaseMenu.get("DatabaseMoreMenu").insert(
    [
        MenuItem(_("International Heat Flow Commission"), url="https://ihfc-iugg.org", icon="globe"),
        MenuItem(_("Portal Team"), view_name="home", icon="contributors"),
    ],
    position=0,
)
