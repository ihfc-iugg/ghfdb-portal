import fairdm
from django.utils.translation import gettext_lazy as _
from fairdm.metadata import Authority, Citation, ModelConfig

from .filters import HeatFlowFilter, HeatFlowSiteFilter
from .forms import HeatFlowSiteForm
from .models import (
    HeatFlow,
    HeatFlowInterval,
    HeatFlowSite,
    IntervalConductivity,
    SurfaceHeatFlow,
    ThermalGradient,
)
from .tables import HeatFlowIntervalTable, HeatFlowSiteTable, HeatFlowTable, SurfaceHeatFlowTable, ThermalGradientTable


class IHFCConfig(ModelConfig):
    """Base metadata/configuration for all models in the GHFDB database."""

    authority = Authority(
        name=_("International Heat Flow Commission"),
        short_name="IHFC",
        website="https://ihfc-iugg.org",
    )
    citation = Citation(
        text="Fuchs, S., et al. (2021). A new database structure for the IHFC Global Heat Flow Database. International Journal of Terrestrial Heat Flow and Applications, 4(1), pp.1-14.",
        doi="https://doi.org/10.31214/ijthfa.v4i1.62",
    )
    repository_url = "https://github.com/ihfc-iugg/ghfdb-portal"


@fairdm.register(HeatFlowSite)
class HeatFlowSiteConfig(IHFCConfig, ModelConfig):
    description = _(
        "A heat flow site is a specific geological location where measurements of subsurface temperature gradients and thermal conductivity are conducted to determine the heat flow, or the rate of heat transfer from the Earth's interior to its surface."
    )
    keywords = []
    filterset_class = HeatFlowSiteFilter
    form_class = HeatFlowSiteForm
    table_class = HeatFlowSiteTable
    # resource_class = SampleWithLocationResource
    fields = [
        "id",
        "dataset",
        "location",
        "name",
        "latitude",
        "longitude",
        "elevation",
        "country",
        "region",
        "continent",
        "domain",
        # "elevation_datum",
        "azimuth",
        "inclination",
        "length",
        "environment",
        ("explo_method", "explo_purpose"),
        "lithology",
        "age",
        "stratigraphy",
    ]
    fieldsets = {
        None: {
            "fields": [
                "name",
                # ("location.latitude", "location.longitude"),
                # "country",
                ("elevation", "elevation_datum"),
                ("azimuth", "inclination"),
                "length",
                "environment",
                ("explo_method", "explo_purpose"),
                "lithology",
                "age",
                "stratigraphy",
            ],
        },
    }


@fairdm.register(HeatFlowInterval)
class HeatFlowIntervalConfig(IHFCConfig, ModelConfig):
    primary_data_fields = ["q"]
    description = _(
        "A heat flow depth interval is a vertical depth interval within the Earth's subsurface, defined by top and bottom depth measurements, over which temperature measurements are taken to determine the terrestrial heat flow at a given location. This interval is used to assess the rate at which heat is conducted from the Earth's interior to the surface. The depth interval is characterized by its vertical extent, which allows for the analysis of temperature gradients and the calculation of heat flux. This data is crucial for understanding geothermal gradients, heat transfer processes, and the thermal structure of the Earth's crust at that location."
    )
    keywords = []
    filterset_options = {"fields": ["name", "lithology", "stratigraphy"]}
    table_class = HeatFlowIntervalTable
    fields = [
        # "id",
        # "dataset",
        ("top", "bottom"),
        ("vertical_depth", "vertical_datum"),
        "lithology",
        "age",
        "stratigraphy",
    ]


@fairdm.register(SurfaceHeatFlow)
class SurfaceHeatFlowConfig(IHFCConfig, ModelConfig):
    primary_data_fields = ["q"]
    description = _(
        "Heat flow refers to the rate at which heat is transferred from the Earth's interior to its surface. Surface heat flow is the representative heat flow for a given location. Heat flow data are crucial for understanding the geothermal gradient, which indicates how temperature increases with depth beneath the Earth's surface. By analyzing heat flow, scientists can assess the thermal properties of subsurface rocks and fluids, determine the heat generation from radioactive decay within the Earth's crust, and evaluate the potential for geothermal energy resources. This data helps identify areas with higher geothermal potential, guiding the development of geothermal power plants."
    )
    keywords = []
    filterset_options = {"fields": ["name", "value", "uncertainty", "corr_HP_flag"]}
    table_class = SurfaceHeatFlowTable
    # table_class = MeasurementTable
    fields = [
        # "id",
        ("value", "uncertainty"),
        "corr_HP_flag",
        "is_ghfdb",
        # ("sample", "dataset"),
        # "sample_type",
        # "location",
        # "name",
        # "latitude",
        # "longitude",
    ]


@fairdm.register(HeatFlow)
class HeatFlowConfig(IHFCConfig, ModelConfig):
    primary_data_fields = ["q"]
    description = _(
        "A child heat flow measurement refers to the heat flow data obtained from a specific, typically vertical, depth interval within a larger dataset, such as that from a borehole. These measurements represent localized heat flow at particular depths, capturing the rate at which heat is conducted through the Earth at that specific interval. By averaging these child measurements across several depth intervals, scientists can determine the overall surface heat flow for the area. Child heat flow measurements are essential for capturing variations in thermal conductivity and temperature gradients within the subsurface, allowing for a more accurate assessment of the Earth's heat flow at the surface."
    )
    keywords = []
    table_class = HeatFlowTable
    filterset_class = HeatFlowFilter
    fields = [
        ("value", "uncertainty"),
        ("thermal_gradient", "thermal_conductivity"),
        "method",
        "expedition",
        ("probe_type", "probe_length"),
        ("probe_penetration", "probe_tilt"),
        "c_comment",
        # "water_temperature",
    ]


@fairdm.register(ThermalGradient)
class ThermalGradientConfig(IHFCConfig, ModelConfig):
    primary_data_fields = ["mean"]
    description = _(
        "Geothermal gradient refers to the rate of temperature change over a given length interval (typically a depth interval). It reflects how heat flows from the Earth's hot interior toward its cooler surface, driven by conduction, convection, and sometimes advection. Thermal gradient is measured in Kelvin per kilometer (K/km) and varies depending on local geological conditions, such as rock composition and tectonic activity. In regions with high geothermal activity, the thermal gradient is larger, whereas stable cratons tend to have lower gradients. Understanding geothermal gradients helps geoscientists study Earth's geothermal energy potential and processes like plate tectonics and mantle convection."
    )
    filterset_options = {
        "fields": [
            "name",
            "value",
            "uncertainty",
            "corrected_value",
            "corrected_uncertainty",
            "method_top",
            "method_bottom",
            "shutin_top",
            "shutin_bottom",
            "correction_top",
            "correction_bottom",
        ]
    }
    table_class = ThermalGradientTable
    keywords = []
    fields = [
        ("value", "uncertainty"),
        ("corrected_value", "corrected_uncertainty"),
        ("method_top", "method_bottom"),
        ("shutin_top", "shutin_bottom"),
        ("correction_top", "correction_bottom"),
        "number",
    ]


@fairdm.register(IntervalConductivity)
class IntervalConductivityConfig(IHFCConfig, ModelConfig):
    primary_data_fields = ["mean"]
    description = _(
        "Thermal conductivity is a measure of a material's ability to conduct heat. In the Earth's subsurface, thermal conductivity values are crucial for understanding how heat is transferred through rocks and sediments. Interval thermal conductivity refers to the thermal conductivity values measured over a specific length interval in the Earth's crust or mantle, typically vertical. These values help geoscientists calculate heat flow rates, assess geothermal energy potential, and model temperature distributions in the subsurface. By analyzing interval thermal conductivity data, researchers can better understand the thermal properties of rocks and sediments at different depths, aiding in the study of Earth's thermal structure and geodynamic processes."
    )
    filterset_options = {
        "fields": [
            "name",
            "value",
            "uncertainty",
            "source",
            "method",
            "saturation",
            "pT_conditions",
            "pT_function",
            "strategy",
        ]
    }
    keywords = []
    fields = [
        ("value", "uncertainty"),
        ("method", "strategy"),
        "source",
        "saturation",
        ("pT_conditions", "pT_function"),
    ]
