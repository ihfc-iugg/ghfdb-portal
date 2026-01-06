from django.utils.translation import gettext as _
from fairdm.menus import SiteNavigation
from flex_menu import MenuItem

SiteNavigation.insert(
    MenuItem(
        name=_("Explore"),
        view_name="ghfdb-explore",
    ),
    position=0,
)
