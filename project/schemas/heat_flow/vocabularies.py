from django.db import models
from django.utils.translation import gettext_lazy as _
from research_vocabs.concepts import ConceptSchemeBuilder, LocalConceptScheme


class SimpleLithology(LocalConceptScheme):
    class Meta:
        source = "simple_lithology.ttl"


class ISC2020(LocalConceptScheme):
    class Meta:
        source = "isc2020.ttl"


class HeatFlowMethodConcept(ConceptSchemeBuilder):
    fourier = {
        "SKOS.prefLabel": _("Fourier's Law"),
        "SKOS.definition": _(
            "Product of the mean thermal gradient to the mean thermal conductivity with reference to a specified depth interval"
        ),
    }
    product = {
        "SKOS.prefLabel": _("Product or Interval"),
        "SKOS.definition": _(
            "Product of the mean thermal gradient to the mean thermal conductivity with reference to a specified depth interval"
        ),
    }
    bullard = {
        "SKOS.prefLabel": _("Bullard"),
        "SKOS.definition": _(
            "Heat-flow value given as the angular coefficient of the linear regression of the thermal resistance vs. temperature data (used when there is a significant variation of thermal conductivity within the depth range over which the temperatures have been measured)"
        ),
    }
    bootstrap = {
        "SKOS.prefLabel": _("Boot-strapping"),
        "SKOS.definition": _(
            "Iterative procedure aimed at minimize the difference between the measured and modelled temperatures by solving the 1-D steady-state conductive geotherm (radiogenic heat production of rocks is accounted for)"
        ),
    }
    other = {
        "SKOS.prefLabel": _("Other"),
        "SKOS.definition": _("Specify the method in comments"),
    }

    class Meta:
        namespace = "https://heatflow.world/vocabularies/"
        namespace_prefix = "ghfdb"
        conceptscheme = {
            "SKOS.altLabel": _("My Material Scheme"),
            "SKOS.prefLabel": _("My Materials"),
            "SKOS.hasTopConcept": [
                "Wood",
                "Metal",
            ],
        }
        # ordered_collections = {"orderedCollectionA": ["Metal", "Plastic", "Wood"]}
        # collections = {
        #     "collectionA": ["Wood", "Metal"],
        #     "collectionB": ["Wood"],
        # }
        # source = "heat_flow_method.ttl"


class HeatFlowMethod(models.TextChoices):
    """Principal method of heat-flow density calculation from temperature and thermal conductivity data. Allowed entries:
    [Fourier's Law or Product or Interval method: product of the mean thermal gradient to the
    mean thermal conductivity with reference to a specified depth interval] /
    [Bullard method: heat-flow value given as the angular coefficient of the linear regression
    of the thermal resistance vs. temperature data (used when there is a significant variation of
    thermal conductivity within the depth range over which the temperatures have been measured)] /
    [Boot-strapping method: iterative procedure aimed at minimize the difference between the
    measured and modelled temperatures by solving the 1-D steady-state conductive geotherm
    (radiogenic heat production of rocks is accounted for)] /
    [other: specify]"""

    FOURIER = "FOU", _("Fourier's Law")
    PRODUCT = "PRO", _("Product or Interval")
    BULLARD = "BUL", _("Bullard")
    BOOTSTRAP = "BOO", _("Boot-strapping")
    OTHER = "OTH", _("Other")


class ProbeType(models.TextChoices):
    """Type of heat-flow probe used for measurement. Name one of the following options:

    [Corer-outrigger] / [Bullard probe] / [Lister Violin-Bow probe] / [Ewing probe] / [Other
    probe] / [Unspecified]"""

    CORER = "COR", _("Corer-outrigger")
    BULLARD = "BUL", _("Bullard")
    VIOLIN_BOW = "VIO", _("Lister Violin-Bow")
    EWING = "EWI", _("Ewing")
    OTHER = "OTH", _("Other")
    UNSPECIFIED = "UNS", _("Unspecified")


class HeatFlowTransferMechanism(models.TextChoices):
    """Specification of the predominant heat transfer mechanism relevant for the reported heatflow value. Possible entries:

    [Conductive] / [Convective unspecified] / [Convective upflow] / [Convective downflow]
    / [unspecified]"""

    CONDUCTIVE = "Conductive", _("Conductive")
    CONVECTIVE = "Convective unspecified", _("Convective unspecified")
    CONVECTIVE_UPFLOW = "Convective upflow", _("Convective upflow")
    CONVECTIVE_DOWNFLOW = "Convective downflow", _("Convective downflow")
    UNSPECIFIED = "unspecified", _("Unspecified")


class GeographicEnvironment(models.TextChoices):
    """Specification of the geographic environment where the heat-flow measurement was performed. Possible entries:

    [Onshore (continental)]
    [Onshore (lake, river, etc.)]
    [Offshore (continental)]
    [Offshore (marine)]
    [unspecified]"""

    ONSHORE_CONTINENTAL = "Onshore (continental)", _("Onshore (continental)")
    ONSHORE_LAKE = "Onshore (lake, river, etc.)", _("Onshore (lake, river, etc.)")
    OFFSHORE_CONTINENTAL = "Offshore (continental)", _("Offshore (continental)")
    OFFSHORE_MARINE = "Offshore (marine)", _("Offshore (marine)")
    UNSPECIFIED = "unspecified", _("Unspecified")


class ExplorationMethod(models.TextChoices):
    """Specification of the general means by which the rock was accessed by temperature sensors for the respective data entry. Possible database entries:
    [Drilling]
    [Mining]
    [Tunneling]
    [Probing (onshore/lake, river, etc.)]
    [Probing (offshore/ocean)]
    [Other (specify in comments)]
    [unspecified]"""

    DRILLING = "Drilling", _("Drilling")
    MINING = "Mining", _("Mining")
    TUNNELING = "Tunneling", _("Tunneling")
    PROBING_ONSHORE = "Probing (onshore/lake, river, etc.)", _("Probing (onshore/lake, river, etc.)")
    PROBING_OFFSHORE = "Probing (offshore/ocean)", _("Probing (offshore/ocean)")
    OTHER = "Other (specify in comments)", _("Other (specify in comments)")
    UNSPECIFIED = "unspecified", _("Unspecified")


class ExplorationPurpose(models.TextChoices):
    """Main purpose of the original excavation providing access for the temperature sensors. Possible database entries:

    [Hydrocarbon]
    [Underground storage]
    [Geothermal]
    [Groundwater]
    [Mapping]
    [Mining]
    [Research]
    [Tunneling]
    [Other (specify in comments)]
    [unspecified]"""

    HYDROCARBON = "Hydrocarbon", _("Hydrocarbon")
    UNDERGROUND_STORAGE = "Underground storage", _("Underground storage")
    GEOTHERMAL = "Geothermal", _("Geothermal")
    GROUNDWATER = "Groundwater", _("Groundwater")
    MAPPING = "Mapping", _("Mapping")
    MINING = "Mining", _("Mining")
    RESEARCH = "Research", _("Research")
    TUNNELING = "Tunneling", _("Tunneling")
    OTHER = "Other (specify in comments)", _("Other (specify in comments)")
    UNSPECIFIED = "unspecified", _("Unspecified")


class TemperatureMethod(models.TextChoices):
    """
    The allowed temperature methods for the T_method_top and T_method_bottom fields at the heat flow child level.


    **Continuous temperature logging** (using semiconductor transducer, or thermistor probe):

    * *LOGeq* - borehole in equilibrium
    * *LOGpert* - borehole perturbed
    * *cLOG* - perturbed but corrected

    **Distributed Temperature Sensing**:

    * *DTSeq* - in equilibrium
    * *DTSpert* - perturbed
    * *cDTS* - perturbed but corrected

    **Bottom Hole Temperature**:

    * *BHT* - uncorrected
    * *cBHT* - corrected

    **Drill stem test**:

    * *DST* - uncorrected
    * *cDST* - corrected for effects

    **Resistance temperature detectors**:

    * *RTDeq* - in equilibrium
    * *RTDpert* - perturbed
    * *cRTD* - perturbed but corrected

    **Ocean Drilling Temperature Tool**:

    * *ODTT-PC* - piston corer
    * *ODTT-TP* - thermistor probe

    **Other**:

    * *CPD* - Curie Point/Depth estimates
    * *XEN* - Xenolith
    * *GTM* - Geothermometry
    * *BSR* - bottom-simulating seismic reflector
    * *SUR* - surface temperature/bottom water temperature
    * *OTH* - other (method must be specified in comments)
    """

    LOGeq = "LOGeq", _("LOGeq: borehole in equilibrium")
    LOGpert = "LOGpert", _("LOGpert: borehole perturbed")
    cLOG = "cLOG", _("cLOG: perturbed but corrected")
    DTSeq = "DTSeq", _("DTSeq: in equilibrium")
    DTSpert = "DTSpert", _("DTSpert: perturbed")
    cDTS = "cDTS", _("cDTS: perturbed but corrected")
    BHT = "BHT", _("BHT: uncorrected")
    cBHT = "cBHT", _("cBHT: corrected")
    DST = "DST", _("DST: uncorrected")
    cDST = "cDST", _("cDST: corrected for effects")
    RTDeq = "RTDeq", _("RTDeq: in equilibrium")
    RTDpert = "RTDpert", _("RTDpert: perturbed")
    cRTD = "cRTD", _("cRTD: perturbed but corrected")
    ODTT_PC = "ODTT-PC", _("ODTT-PC: piston corer")
    ODTT_TP = "ODTT-TP", _("ODTT-TP: thermistor probe")
    CPD = "CPD", _("CPD: Curie Point/Depth estimates")
    XEN = "XEN", _("XEN: Xenolith")
    GTM = "GTM", _("GTM: Geothermometry")
    BSR = "BSR", _("BSR: bottom-simulating seismic reflector")
    SUR = "SUR", _("SUR: surface temperature/bottom water temperature")
    OTH = "OTH", _("Other (method must be specified in comments)")


class TemperatureCorrection(models.TextChoices):
    """[Horner plot]
    [Cylinder source method]
    [Line source explosion method]
    [Inverse numerical modelling]
    [Other published correction]
    [unspecified]
    [not corrected]"""

    HORNER = "Horner plot", _("Horner plot")
    CYLINDER = "Cylinder source method", _("Cylinder source method")
    LINE = "Line source explosion method", _("Line source explosion method")
    INVERSE = "Inverse numerical modelling", _("Inverse numerical modelling")
    OTHER = "Other published correction", _("Other published correction")
    UNSPECIFIED = "unspecified", _("Unspecified")
    NOT_CORRECTED = "not corrected", _("Not corrected")


class ConductivitySource(models.TextChoices):
    """[In-situ probe]
    [Core-log integration]
    [Core samples]
    [Cutting samples]
    [Outcrop samples]
    [Well-log interpretation]
    [Mineral computation]
    [Assumed from literature]
    [other (specify)]
    [unspecified]"""

    INSITU_PROBE = "In-situ probe", _("In-situ probe")
    CORE_LOG = "Core-log integration", _("Core-log integration")
    CORE_SAMPLES = "Core samples", _("Core samples")
    CUTTING_SAMPLES = "Cutting samples", _("Cutting samples")
    OUTCROP_SAMPLES = "Outcrop samples", _("Outcrop samples")
    WELL_LOG = "Well-log interpretation", _("Well-log interpretation")
    MINERAL_COMPUTATION = "Mineral computation", _("Mineral computation")
    ASSUMED_FROM_LITERATURE = "Assumed from literature", _("Assumed from literature")
    OTHER = "Other (specify)", _("Other (specify)")
    UNSPECIFIED = "unspecified", _("Unspecified")


class ConductivityMethod(models.TextChoices):
    """
    Laboratory Methods:

        - [Lab - point source]
        - [Lab - line source / full space]
        - [Lab - line source / half space]
        - [Lab - plane source / full space]
        - [Lab - plane source / half space]
        - [Lab - other]

    Probe Methods:

        [Probe - pulse technique]

    Well-log Methods:

        [Well-log - deterministic approach]
        [Well-log - empirical equation]

    Estimation Methods:

        [Estimation - from chlorine content]
        [Estimation - from water content/porosity]
        [Estimation - from lithology and literature]
        [Estimation - from mineral composition]

    Other:

        [unspecified]

    """

    LAB_POINT = "Lab - point source", _("Lab - point source")
    LAB_LINE_FULL = "Lab - line source / full space", _("Lab - line source / full space")
    LAB_LINE_HALF = "Lab - line source / half space", _("Lab - line source / half space")
    LAB_PLANE_FULL = "Lab - plane source / full space", _("Lab - plane source / full space")
    LAB_PLANE_HALF = "Lab - plane source / half space", _("Lab - plane source / half space")
    LAB_OTHER = "Lab - other", _("Lab - other")
    PROBE_PULSE = "Probe - pulse technique", _("Probe - pulse technique")
    WELL_LOG_DETERMINISTIC = "Well-log - deterministic approach", _("Well-log - deterministic approach")
    WELL_LOG_EMPIRICAL = "Well-log - empirical equation", _("Well-log - empirical equation")
    ESTIMATION_CHLORINE = "Estimation - from chlorine content", _("Estimation - from chlorine content")
    ESTIMATION_WATER = "Estimation - from water content/porosity", _("Estimation - from water content/porosity")
    ESTIMATION_LITHOLOGY = "Estimation - from lithology and literature", _("Estimation - from lithology and literature")
    ESTIMATION_MINERAL = "Estimation - from mineral composition", _("Estimation - from mineral composition")
    UNSPECIFIED = "unspecified", _("Unspecified")


ConductivityMethodFormChoices = [
    (
        _("Laboratory"),
        [
            ConductivityMethod.LAB_POINT,
            ConductivityMethod.LAB_LINE_FULL,
            ConductivityMethod.LAB_LINE_HALF,
            ConductivityMethod.LAB_PLANE_FULL,
            ConductivityMethod.LAB_PLANE_HALF,
            ConductivityMethod.LAB_OTHER,
        ],
    ),
    (
        _("Probe"),
        [
            ConductivityMethod.PROBE_PULSE,
        ],
    ),
    (
        _("Well-log"),
        [
            ConductivityMethod.WELL_LOG_DETERMINISTIC,
            ConductivityMethod.WELL_LOG_EMPIRICAL,
        ],
    ),
    (
        _("Estimation"),
        [
            ConductivityMethod.ESTIMATION_CHLORINE,
            ConductivityMethod.ESTIMATION_WATER,
            ConductivityMethod.ESTIMATION_LITHOLOGY,
            ConductivityMethod.ESTIMATION_MINERAL,
        ],
    ),
    (
        _("Other"),
        [
            ConductivityMethod.UNSPECIFIED,
        ],
    ),
]


class ConductivityLocation(models.TextChoices):
    """
    [Actual heat-flow location]
    [Other location]
    [Literature/unspecified]"""

    ACTUAL = "Actual heat-flow location", _("Actual heat-flow location")
    OTHER = "Other location", _("Other location")
    LITERATURE = "Literature/unspecified", _("Literature/unspecified")


class ConductivitySaturation(models.TextChoices):
    """
    Saturated measured insitu: Insitu saturated measured (measurements with probe sensing / marine measurements).
    Recovered: As recovered (rocks have been preserved and measured in close to their natural saturation state).
    Saturated measured: Saturated measured (rocks have been technically saturated completely before measurement).
    Saturated calculated: Saturated calculated (thermal conductivity has been calculated from dry measured rocks, porosity and pore-filling fluid).
    Dry measured: Dry measured - rocks have been technically dried before measurement.
    Other: Other saturation state (must be specified in comments).
    Unspecified: Unspecified.
    """

    SATURATED_IN_SITU = "Saturated measured in-situ", _("Saturated measured in-situ")
    RECOVERED = "Recovered", _("Recovered")
    SATURATED_MEASURED = "Saturated measured", _("Saturated measured")
    SATURATED_CALCULATED = "Saturated calculated", _("Saturated calculated")
    DRY_MEASURED = "Dry measured", _("Dry measured")
    OTHER = "Other (specify)", _("Other (must be specified in comments)")
    UNSPECIFIED = "Unspecified", _("Unspecified")


class ConductivityPTConditions(models.TextChoices):
    """
    - "Recorded" - determinations under true conditions at target depths (e.g. sensing in boreholes)
    - "Replicated conditions" - determinations where the conditions at target depths are replicated under laboratory conditions
    - "Corrected conditions" - determinations under laboratory pT conditions that were corrected to conditions at target depths
    - "Actual" - the condition at the respective depth of the heat-flow interval.

    [Unrecorded ambient pT conditions]
    [Recorded ambient pT conditions]
    [Actual in-situ (pT) conditions]
    [Replicated in-situ (p)]
    [Replicated in-situ (T)]
    [Replicated in-situ (pT)]
    [Corrected in-situ (p)]
    [Corrected in-situ (T)]
    [Corrected in-situ (pT)]
    [unspecified]"""

    UNRECORDED = "Unrecorded ambient pT conditions", _("Unrecorded ambient pT conditions")
    RECORDED = "Recorded ambient pT conditions", _("Recorded ambient pT conditions")
    ACTUAL = "Actual in-situ (pT) conditions", _("Actual in-situ (pT) conditions")
    REPLICATED_P = "Replicated in-situ (p)", _("Replicated in-situ (p)")
    REPLICATED_T = "Replicated in-situ (T)", _("Replicated in-situ (T)")
    REPLICATED_PT = "Replicated in-situ (pT)", _("Replicated in-situ (pT)")
    CORRECTED_P = "Corrected in-situ (p)", _("Corrected in-situ (p)")
    CORRECTED_T = "Corrected in-situ (T)", _("Corrected in-situ (T)")
    CORRECTED_PT = "Corrected in-situ (pT)", _("Corrected in-situ (pT)")
    UNSPECIFIED = "unspecified", _("Unspecified")


class ConductivityStrategy(models.TextChoices):
    """[Random or periodic depth sampling (number)]
    [Characterize formation conductivities]
    [Well log interpretation]
    [Computation from probe sensing]
    [Other]
    [unspecified]"""

    RANDOM = "Random or periodic depth sampling (number)", _("Random or periodic depth sampling (number)")
    CHARACTERIZE = "Characterize formation conductivities", _("Characterize formation conductivities")
    WELL_LOG = "Well log interpretation", _("Well log interpretation")
    COMPUTATION = "Computation from probe sensing", _("Computation from probe sensing")
    OTHER = "Other", _("Other")
    UNSPECIFIED = "unspecified", _("Unspecified")


# class ConductivityPTFunction(models.TextChoices):
#     """
#     [T - Tikhomirov (1968)]
#     [T - Kutas & Gordienko (1971)]
#     [T - Anand et al. (1973)]
#     [T - Haenel & Zoth (1973)]
#     [T - Blesch et al. (1983)]
#     [T - Sekiguchi (1984)]
#     [T - Chapman et al. (1984)]
#     [T - Zoth & Haenel (1988)]
#     [T - Somerton (1992)]
#     [T - Sass et al. (1992)]
#     [T - Funnell et al. (1996)]
#     [T - Kukkonen et al. (1999)]
#     [T - Seipold (2001)]
#     [T - Vosteen & Schellschmidt (2003)]
#     [T - Sun et al. (2017)]
#     [T - Miranda et al. (2018)]
#     [T - Ratcliff (1960)]
#     [p - Bridgman (1924)]
#     [p - Sibbitt (1975)]
#     [p - Kukkonen et al. (1999)]
#     [p - Seipold (2001)]
#     [p - Durutürk et al. (2002)]
#     [p - Demirci et al. (2004)]
#     [p - Görgülü et al. (2008)]
#     [p - Fuchs & Förster (2014)]
#     [pT - Radcliff (1960)]
#     [pT - Buntebarth (1991)]
#     [pT - Chapman & Furlong (1992)]
#     [pT - Emirov et al. (1997)]
#     [pT - Abdulagatov et al. (2006)]
#     [pT - Emirov & Ramazanova (2007)]
#     [pT - Abdulagatova et al. (2009)]
#     [pT - Ramazanova & Emirov (2010)]
#     [pT - Ramazanova & Emirov (2012)]
#     [pT - Emirov et al. (2017)]
#     [Site-specific experimental relationships]
#     [Other (specify in comments)]
#     [Unspecified]
#     """

#     TIKHOMIROV = "T - Tikhomirov (1968)", "T - Tikhomirov (1968)"
#     KUTAS


ConductivityPTFunction = [
    (x, x)
    for x in [
        "T - Tikhomirov (1968)",
        "T - Kutas & Gordienko (1971)",
        "T - Anand et al. (1973)",
        "T - Haenel & Zoth (1973)",
        "T - Blesch et al. (1983)",
        "T - Sekiguchi (1984)",
        "T - Chapman et al. (1984)",
        "T - Zoth & Haenel (1988)",
        "T - Somerton (1992)",
        "T - Sass et al. (1992)",
        "T - Funnell et al. (1996)",
        "T - Kukkonen et al. (1999)",
        "T - Seipold (2001)",
        "T - Vosteen & Schellschmidt (2003)",
        "T - Sun et al. (2017)",
        "T - Miranda et al. (2018)",
        "T - Ratcliff (1960)",
        "p - Bridgman (1924)",
        "p - Sibbitt (1975)",
        "p - Kukkonen et al. (1999)",
        "p - Seipold (2001)",
        "p - Durutürk et al. (2002)",
        "p - Demirci et al. (2004)",
        "p - Görgülü et al. (2008)",
        "p - Fuchs & Förster (2014)",
        "pT - Radcliff (1960)",
        "pT - Buntebarth (1991)",
        "pT - Chapman & Furlong (1992)",
        "pT - Emirov et al. (1997)",
        "pT - Abdulagatov et al. (2006)",
        "pT - Emirov & Ramazanova (2007)",
        "pT - Abdulagatova et al. (2009)",
        "pT - Ramazanova & Emirov (2010)",
        "pT - Ramazanova & Emirov (2012)",
        "pT - Emirov et al. (2017)",
    ]
] + [
    ("Site-specific experimental relationships", _("Site-specific experimental relationships")),
    ("Other", _("Other (specify in comments)")),
    ("Unspecified", _("Unspecified")),
]


# ConductivityPTFunction = [
#     (
#         _("Temperature Only"),
#         [
#             (x, x)
#             for x in [
#                 "T - Tikhomirov (1968)",
#                 "T - Kutas & Gordienko (1971)",
#                 "T - Anand et al. (1973)",
#                 "T - Haenel & Zoth (1973)",
#                 "T - Blesch et al. (1983)",
#                 "T - Sekiguchi (1984)",
#                 "T - Chapman et al. (1984)",
#                 "T - Zoth & Haenel (1988)",
#                 "T - Somerton (1992)",
#                 "T - Sass et al. (1992)",
#                 "T - Funnell et al. (1996)",
#                 "T - Kukkonen et al. (1999)",
#                 "T - Seipold (2001)",
#                 "T - Vosteen & Schellschmidt (2003)",
#                 "T - Sun et al. (2017)",
#                 "T - Miranda et al. (2018)",
#                 "T - Ratcliff (1960)",
#             ]
#         ],
#     ),
#     (
#         _("Pressure Only"),
#         [
#             (x, x)
#             for x in [
#                 "p - Bridgman (1924)",
#                 "p - Sibbitt (1975)",
#                 "p - Kukkonen et al. (1999)",
#                 "p - Seipold (2001)",
#                 "p - Durutürk et al. (2002)",
#                 "p - Demirci et al. (2004)",
#                 "p - Görgülü et al. (2008)",
#                 "p - Fuchs & Förster (2014)",
#             ]
#         ],
#     ),
#     (
#         _("Temperature and Pressure"),
#         [
#             (x, x)
#             for x in [
#                 "pT - Radcliff (1960)",
#                 "pT - Buntebarth (1991)",
#                 "pT - Chapman & Furlong (1992)",
#                 "pT - Emirov et al. (1997)",
#                 "pT - Abdulagatov et al. (2006)",
#                 "pT - Emirov & Ramazanova (2007)",
#                 "pT - Abdulagatova et al. (2009)",
#                 "pT - Ramazanova & Emirov (2010)",
#                 "pT - Ramazanova & Emirov (2012)",
#                 "pT - Emirov et al. (2017)",
#             ]
#         ],
#     ),
#     (
#         _("Other"),
#         [
#             ("Site-specific experimental relationships", _("Site-specific experimental relationships")),
#             ("Other", _("Other (specify in comments)")),
#             ("Unspecified", _("Unspecified")),
#         ],
#     ),
# ]


class GenericFlagChoices(models.TextChoices):
    """
    [Present and corrected]
    [Present and not corrected]
    [Present not significant]
    [not recognized]
    [unspecified]"""

    PRESENT_CORRECTED = "Present and corrected", _("Present and corrected")
    PRESENT_NOT_CORRECTED = "Present and not corrected", _("Present and not corrected")
    PRESENT_NOT_SIGNIFICANT = "Present not significant", _("Present not significant")
    NOT_RECOGNIZED = "not recognized", _("Not recognized")
    UNSPECIFIED = "unspecified", _("Unspecified")


class InSituFlagChoices(models.TextChoices):
    """
    [Considered - p]
    [Considered - T]
    [Considered - pT]
    [not Considered ]
    [unspecified]"""

    CONSIDERED_P = "Considered - p", _("Considered - p")
    CONSIDERED_T = "Considered - T", _("Considered - T")
    CONSIDERED_PT = "Considered - pT", _("Considered - pT")
    NOT_CONSIDERED = "not Considered", _("Not considered")
    UNSPECIFIED = "unspecified", _("Unspecified")


class TemperatureFlagChoices(models.TextChoices):
    """
    [Tilt corrected]
    [Drift corrected]
    [not corrected]
    [Corrected (specify)]
    [unspecified]"""

    TILT_CORRECTED = "Tilt corrected", _("Tilt corrected")
    DRIFT_CORRECTED = "Drift corrected", _("Drift corrected")
    NOT_CORRECTED = "not corrected", _("Not corrected")
    CORRECTED = "Corrected (specify)", _("Corrected (specify)")
    UNSPECIFIED = "unspecified", _("Unspecified")
