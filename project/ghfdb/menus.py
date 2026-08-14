from django.utils.translation import gettext as _
from fairdm.menus import AppMenu
from flex_menu import Menu, MenuItem

AppMenu.insert(
    MenuItem(
        name=_("GHFDB Map Viewer"),
        view_name="ghfdb-explore",
        extra_context={"icon": "map"},
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
