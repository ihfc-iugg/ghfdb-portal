"""Navigation menu entries for the GHFDB app."""

from django.utils.translation import gettext_lazy as _
from fairdm.menus import AppMenu
from flex_menu import Menu, MenuItem
from mvp.menus import MenuCollapse

AppMenu.insert(
    MenuCollapse(
        name="ghfdb",
        extra_context={"label": _("GHFDB"), "icon": "database"},
        children=[
            MenuItem(
                name="ghfdb_map_viewer",
                view_name="ghfdb-explore",
                extra_context={"label": _("Map Viewer"), "icon": "map"},
            ),
            MenuItem(
                name="ghfdb_parent_table",
                view_name="ghfdb-parent-table",
                extra_context={"label": _("Parent Table"), "icon": "table"},
            ),
        ],
    ),
    position=1,
)

LearnMoreMenu = Menu(
    name=_("Learn More"),
    children=[
        MenuItem(
            name=_("GitHub Repository"),
            url="https://github.com/ihfc-iugg/ghfdb-portal",
            extra_context={"icon": "github"},
        ),
        MenuItem(
            name=_("Portal Documentation"),
            url="https://heatflowworld.readthedocs.io/en/latest/",
            extra_context={"icon": "literature"},
        ),
        MenuItem(
            name=_("WHFDB Project Website"),
            url="https://heatflow.world/",
            extra_context={"icon": "external_link"},
        ),
        MenuItem(
            name=_("IHFC Website"),
            url="https://ihfc-iugg.com/",
            extra_context={"icon": "ihfc"},
        ),
    ],
)


AppMenu.append(LearnMoreMenu)
