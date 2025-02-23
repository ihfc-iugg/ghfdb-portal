from django.utils.translation import gettext as _
from fairdm.menus import DatabaseMenu
from flex_menu import Menu, MenuItem

DatabaseMenu.insert(
    [
        Menu(
            "MapMenu",
            template="fairdm/menus/database/menu.html",
            label=None,
            children=[
                # MenuItem(_("Global Heat Flow Database"), view_name="map", icon="map"),
                MenuItem(
                    _("Global Heat Flow Database"),
                    url="https://worldheatflowdatabase.github.io/HeatFlowMapping/",
                    icon="map",
                ),
            ],
        ),
    ],
    position=0,
)


DatabaseMenu.get("DatabaseMoreMenu").insert(
    [
        MenuItem(_("International Heat Flow Commission"), url="https://ihfc-iugg.org", icon="globe"),
        MenuItem(_("HeatFlow.world"), url="https://heatflow.world", icon="globe"),
        MenuItem(_("Team"), url="https://www.heatflow.world/about/team", icon="contributors"),
    ],
    position=0,
)


DatabaseMenu.get("Literature").check = False
DatabaseMenu.get("Contributors").check = False
