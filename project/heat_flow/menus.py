from django.utils.translation import gettext as _
from fairdm.menus import NavLink, SiteNavigation

SiteNavigation.insert(
    [
        NavLink(
            _("Explore"),
            view_name="ghfdb-explore",
        ),
    ],
    position=1,
)
