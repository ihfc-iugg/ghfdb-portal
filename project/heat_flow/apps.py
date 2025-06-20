from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from fairdm.metadata import Authority, Citation


class HeatFlowSchemaConfig(AppConfig):
    """Config for heat flow schema"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "heat_flow"
    verbose_name = _("Heat Flow")

    authority = Authority(
        name=_("International Heat Flow Commission"),
        short_name="IHFC",
        website="https://ihfc-iugg.org",
    )
    citation = Citation(
        text="Fuchs, S., et al. (2021). A new database structure for the IHFC Global Heat Flow Database. International Journal of Terrestrial Heat Flow and Applications, 4(1), pp.1-14.",
        doi="https://doi.org/10.31214/ijthfa.v4i1.62",
    )
    keywords = []
    repository_url = "https://github.com/ihfc-iugg/ghfdb-portal"

    # SurfaceHeatFlow = {"list_display": ["q", "q_uncertainty"]}
    # HeatFlow = {}
