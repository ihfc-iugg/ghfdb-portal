from django.utils.translation import gettext as _
from fairdm.menus import SiteNavigation, SubMenuItem

literature_menu = SiteNavigation.get("More")
literature_menu.insert(
    [
        SubMenuItem(
            _("Literature Review"),
            view_name="review-list",
        ),
    ],
    position=1,
)
