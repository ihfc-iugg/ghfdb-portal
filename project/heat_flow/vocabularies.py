from django.utils.translation import gettext_lazy as _
from research_vocabs.builder.skos import Collection, Concept
from research_vocabs.vocabularies import VocabularyBuilder

BASE_NAMESPACE = "https://heatflow.world/vocabularies/"


class HeatFlowMethod(VocabularyBuilder):
    fourier = Concept(
        prefLabel=_("Fourier's Law"),
        definition=_(
            "Product of the mean thermal gradient to the mean thermal conductivity with reference to a specified depth interval"
        ),
    )

    product = Concept(
        prefLabel=_("Product method"),
        definition=_(
            "Product of the mean thermal gradient to the mean thermal conductivity with reference to a specified depth interval"
        ),
    )

    interval = Concept(
        prefLabel=_("Interval method"),
        definition=_(
            "Product of the mean thermal gradient to the mean thermal conductivity with reference to a specified depth interval"
        ),
    )

    bullard = Concept(
        prefLabel=_("Bullard method"),
        definition=_(
            "Heat-flow value given as the angular coefficient of the linear regression of the thermal resistance vs. temperature data (used when there is a significant variation of thermal conductivity within the depth range over which the temperatures have been measured)"
        ),
    )

    bootstrap = Concept(
        prefLabel=_("Boot-strapping method"),
        definition=_(
            "Iterative procedure aimed at minimize the difference between the measured and modelled temperatures by solving the 1-D steady-state conductive geotherm (radiogenic heat production of rocks is accounted for)"
        ),
    )

    other = Concept(
        prefLabel=_("Other"),
        definition=_("Specify the method in comments"),
    )

    class Meta:
        name = "heat-flow-method"
        prefix = "ghfdb"
        namespace = BASE_NAMESPACE + name + "/"
        scheme_attrs = {
            "skos:prefLabel": _("Heat flow methods"),
            "skos:definition": _("Methods used to determine heat flow."),
        }


# [Single Steel probe (Bullard)]
# [Single Steel probe (Bullard) in-situ TC]
# [Violin-Bow probe (Lister)]
# [Outrigger probe (Von Herzen) in-situ TC, without corer]
# [Outrigger probe (Ewing) with corer]
# [Outrigger probe (autonomous) without corer]
# [Outrigger probe (autonomous) with corer]
# [Submersible probe]
# [Other (specify in comments)]
# [unspecified]


class ProbeType(VocabularyBuilder):
    """Type of heat-flow probe used for measurement."""

    corer = Concept(
        prefLabel=_("Corer-outrigger"),
        definition=_(""),
    )

    bullard = Concept(
        prefLabel=_("Bullard probe"),
        definition=_(""),
    )

    violin_bow = Concept(
        prefLabel=_("Lister Violin-Bow probe"),
        definition=_(""),
    )

    ewing = Concept(
        prefLabel=_("Ewing probe"),
        definition=_(""),
    )

    other = Concept(
        prefLabel=_("Other probe"),
        definition=_(""),
    )

    unspecified = Concept(
        prefLabel=_("Unspecified"),
        definition=_(""),
    )

    class Meta:
        name = "heat-flow-probes"
        prefix = "ghfdb"
        namespace = BASE_NAMESPACE + name + "/"
        scheme_attrs = {
            "skos:prefLabel": _("Heat flow probe types"),
            "skos:definition": _(
                "Types of heat-flow probes used for collecting heat flow data, typically in marine settings."
            ),
        }


class HeatFlowTransferMechanism(VocabularyBuilder):
    """Specification of the predominant heat transfer mechanism relevant for the reported heatflow value."""

    conductive = Concept(
        prefLabel=_("Conductive"),
        definition=_(""),
    )

    convective = Concept(
        prefLabel=_("Convective unspecified"),
        definition=_(""),
    )

    upflow = Concept(
        prefLabel=_("Convective upflow"),
        definition=_(""),
    )

    downflow = Concept(
        prefLabel=_("Convective downflow"),
        definition=_(""),
    )

    unspecified = Concept(
        prefLabel=_("Unspecified"),
        definition=_(""),
    )

    class Meta:
        name = "transfer-mechanisms"
        prefix = "ghfdb"
        namespace = BASE_NAMESPACE + name + "/"
        scheme_attrs = {
            "skos:prefLabel": _("Heat-flow specific transfer mechanisms"),
            "skos:definition": _("Mechanisms of heat transfer though the Earth's crust."),
        }


class GeographicEnvironment(VocabularyBuilder):
    """Specification of the geographic environment where the heat-flow measurement was performed."""

    onshore_continental = Concept(
        prefLabel=_("Onshore (continental)"),
        definition=_(""),
    )

    onshore_lake = Concept(
        prefLabel=_("Onshore (lake, river, etc.)"),
        definition=_(""),
    )

    offshore_continental = Concept(
        prefLabel=_("Offshore (continental)"),
        definition=_(""),
    )

    offshore_marine = Concept(
        prefLabel=_("Offshore (marine)"),
        definition=_(
            "An offshore marine environment refers to the part of the ocean that is beyond the coastal zone, typically starting from the edge of the continental shelf and extending into the open ocean. It includes deep-sea regions, open waters, and underwater ecosystems such as seamounts, mid-ocean ridges, and abyssal plains."
        ),
    )

    unspecified = Concept(
        prefLabel=_("Unspecified"),
        definition=_(""),
    )

    class Meta:
        name = "geographic-environments"
        prefix = "ghfdb"
        namespace = BASE_NAMESPACE + name + "/"
        scheme_attrs = {
            "skos:prefLabel": _("geographic environments"),
            "skos:definition": _("Basic geographic environments where heat-flow measurements are performed."),
        }

        collections = {
            "onshore": Collection(
                prefLabel=_("Onshore environments"),
                definition=_("Geographic environments found onshore."),
                members=["onshore_continental", "onshore_lake"],
            ),
            "offshore": Collection(
                prefLabel=_("Offshore environments"),
                definition=_("Geographic environments found offshore."),
                members=["offshore_continental", "offshore_marine"],
            ),
        }


class ExplorationMethod(VocabularyBuilder):
    """Specification of the general means by which the rock was accessed by temperature sensors for the respective data entry."""

    drilling = Concept(
        prefLabel=_("Drilling"),
        definition=_(""),
    )

    mining = Concept(
        prefLabel=_("Mining"),
        definition=_(""),
    )

    tunneling = Concept(
        prefLabel=_("Tunneling"),
        definition=_(""),
    )

    probing_onshore = Concept(
        prefLabel=_("Probing (onshore/lake, river, etc.)"),
        definition=_(""),
    )

    probing_offshore = Concept(
        prefLabel=_("Probing (offshore/ocean)"),
        definition=_(""),
    )

    other = Concept(
        prefLabel=_("Other (specify in comments)"),
        definition=_(""),
    )

    unspecified = Concept(
        prefLabel=_("Unspecified"),
        definition=_(""),
    )

    class Meta:
        name = "exploration-methods"
        prefix = "ghfdb"
        namespace = BASE_NAMESPACE + name + "/"
        scheme_attrs = {
            "skos:prefLabel": _("exploration methods"),
            "skos:definition": _("General means by which the rock was accessed by temperature sensors."),
        }


class ExplorationPurpose(VocabularyBuilder):
    """Main purpose of the original excavation providing access for the temperature sensors."""

    hydrocarbon = Concept(
        prefLabel=_("Hydrocarbon"),
        definition=_(""),
    )

    underground_storage = Concept(
        prefLabel=_("Underground storage"),
        definition=_(""),
    )

    geothermal = Concept(
        prefLabel=_("Geothermal"),
        definition=_(""),
    )

    groundwater = Concept(
        prefLabel=_("Groundwater"),
        definition=_(""),
    )

    mapping = Concept(
        prefLabel=_("Mapping"),
        definition=_(""),
    )

    mining = Concept(
        prefLabel=_("Mining"),
        definition=_(""),
    )

    research = Concept(
        prefLabel=_("Research"),
        definition=_(""),
    )

    tunneling = Concept(
        prefLabel=_("Tunneling"),
        definition=_(""),
    )

    other = Concept(
        prefLabel=_("Other (specify in comments)"),
        definition=_(""),
    )

    unspecified = Concept(
        prefLabel=_("Unspecified"),
        definition=_(""),
    )

    class Meta:
        name = "exploration-purpose"
        namespace = BASE_NAMESPACE + name + "/"
        prefix = "ghfdb"
        scheme_attrs = {
            "skos:prefLabel": _("Exploration purposes"),
            "skos:definition": _(
                "Main purpose of the original excavation providing access for the temperature sensors."
            ),
        }


class TemperatureMethod(VocabularyBuilder):
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

    LOGeq = Concept(
        prefLabel=_("LOGeq: borehole in equilibrium"),
    )
    LOGpert = Concept(
        prefLabel=_("LOGpert: borehole perturbed"),
    )
    cLOG = Concept(
        prefLabel=_("cLOG: perturbed but corrected"),
    )
    DTSeq = Concept(
        prefLabel=_("DTSeq: in equilibrium"),
    )
    DTSpert = Concept(
        prefLabel=_("DTSpert: perturbed"),
    )
    cDTS = Concept(
        prefLabel=_("cDTS: perturbed but corrected"),
    )
    BHT = Concept(
        prefLabel=_("BHT: uncorrected"),
    )
    cBHT = Concept(
        prefLabel=_("cBHT: corrected"),
    )
    DST = Concept(
        prefLabel=_("DST: uncorrected"),
    )
    cDST = Concept(
        prefLabel=_("cDST: corrected"),
    )
    RTDeq = Concept(
        prefLabel=_("RTDeq: in equilibrium"),
    )
    RTDpert = Concept(
        prefLabel=_("RTDpert: perturbed"),
    )
    cRTD = Concept(
        prefLabel=_("cRTD: perturbed but corrected"),
    )
    ODTT_PC = Concept(
        prefLabel=_("ODTT-PC"),
    )
    ODTT_TP = Concept(
        prefLabel=_("ODTT-TP"),
    )
    CPD = Concept(
        prefLabel=_("CPD: Curie Point/Depth estimates"),
    )
    XEN = Concept(
        prefLabel=_("XEN: Xenolith"),
    )
    GTM = Concept(
        prefLabel=_("GTM: Geothermometry"),
    )
    BSR = Concept(
        prefLabel=_("BSR: bottom-simulating seismic reflector"),
    )
    SUR = Concept(
        prefLabel=_("SUR: surface temperature/bottom water temperature"),
    )
    OTH = Concept(
        prefLabel=_("Other (method must be specified in comments)"),
    )

    class Meta:
        name = "temperature-method"
        namespace = BASE_NAMESPACE + name + "/"
        prefix = "ghfdb"
        scheme_attrs = {
            "skos:prefLabel": _("Temperature determination method"),
            "skos:definition": _("Methods used to determine temperature for the purpose of deriving heat flow."),
        }


class TemperatureCorrection(VocabularyBuilder):
    """Specification of the method used to correct the temperature data."""

    hornerPlot = Concept(
        prefLabel=_("Horner plot"),
        definition=_(""),
    )

    cylinderSource = Concept(
        prefLabel=_("Cylinder source method"),
        definition=_(""),
    )

    lineSourceExplosion = Concept(
        prefLabel=_("Line source explosion method"),
        definition=_(""),
    )

    inverseNM = Concept(
        prefLabel=_("Inverse numerical modelling"),
        definition=_(""),
    )

    other = Concept(
        prefLabel=_("Other published correction"),
        definition=_(""),
    )

    unspecified = Concept(
        prefLabel=_("Unspecified"),
        definition=_(""),
    )

    not_corrected = Concept(
        prefLabel=_("not corrected"),
        definition=_(""),
    )

    class Meta:
        name = "temperature-corrections"
        namespace = BASE_NAMESPACE + name + "/"
        prefix = "ghfdb"
        scheme_attrs = {
            "skos:prefLabel": _("Temperature correction methods"),
            "skos:definition": _("Methods used to correct temperature data for the purpose of heat flow measurements."),
        }


class ConductivitySource(VocabularyBuilder):
    """Specification of the source of the thermal conductivity data."""

    insitu_probe = Concept(
        prefLabel=_("In-situ probe"),
        definition=_(""),
    )

    core_log = Concept(
        prefLabel=_("Core-log integration"),
        definition=_(""),
    )

    core_samples = Concept(
        prefLabel=_("Core samples"),
        definition=_(""),
    )

    cutting_samples = Concept(
        prefLabel=_("Cutting samples"),
        definition=_(""),
    )

    outcrop_samples = Concept(
        prefLabel=_("Outcrop samples"),
        definition=_(""),
    )

    well_log = Concept(
        prefLabel=_("Well-log interpretation"),
        definition=_(""),
    )

    mineral_computation = Concept(
        prefLabel=_("Mineral computation"),
        definition=_(""),
    )

    assumed_from_literature = Concept(
        prefLabel=_("Assumed from literature"),
        definition=_(""),
    )

    other = Concept(
        prefLabel=_("Other (specify)"),
        definition=_(""),
    )

    unspecified = Concept(
        prefLabel=_("Unspecified"),
        definition=_(""),
    )

    class Meta:
        name = "conductivity-sources"
        namespace = BASE_NAMESPACE + name + "/"
        prefix = "ghfdb"
        scheme_attrs = {
            "skos:prefLabel": _("conductivity sources"),
        }
        collections = {
            "laboratory": Collection(
                prefLabel=_("Laboratory"),
                definition=_("Laboratory measurements"),
                members=[
                    "core_log",
                    "core_samples",
                    "cutting_samples",
                    "outcrop_samples",
                ],
            ),
            "in_situ": Collection(
                prefLabel=_("In-situ"),
                definition=_("In-situ measurements"),
                members=[
                    "insitu_probe",
                    "well_log",
                ],
            ),
            "computation": Collection(
                prefLabel=_("Computation"),
                definition=_("Computed values"),
                members=[
                    "mineral_computation",
                    "assumed_from_literature",
                ],
            ),
        }


class ConductivityMethod(VocabularyBuilder):
    """Specification of the method used to determine the thermal conductivity."""

    pointSource = Concept(
        prefLabel=_("Lab - point source"),
        definition=_(""),
    )

    lineSourceFull = Concept(
        prefLabel=_("Lab - line source / full space"),
        definition=_(""),
    )

    lineSourceHalf = Concept(
        prefLabel=_("Lab - line source / half space"),
        definition=_(""),
    )

    planeSourceFull = Concept(
        prefLabel=_("Lab - plane source / full space"),
        definition=_(""),
    )

    planeSourceHalf = Concept(
        prefLabel=_("Lab - plane source / half space"),
        definition=_(""),
    )

    laboratoryOther = Concept(
        prefLabel=_("Lab - other"),
        definition=_(""),
    )

    probePulse = Concept(
        prefLabel=_("Probe - pulse technique"),
        definition=_(""),
    )

    wellLogDeterministic = Concept(
        prefLabel=_("Well-log - deterministic approach"),
        definition=_(""),
    )

    wellLogEmpirical = Concept(
        prefLabel=_("Well-log - empirical equation"),
        definition=_(""),
    )

    chlorineContent = Concept(
        prefLabel=_("Estimation - from chlorine content"),
        definition=_(""),
    )

    waterContent = Concept(
        prefLabel=_("Estimation - from water content/porosity"),
        definition=_(""),
    )

    lithology = Concept(
        prefLabel=_("Estimation - from lithology and literature"),
        definition=_(""),
    )

    mineralComposition = Concept(
        prefLabel=_("Estimation - from mineral composition"),
        definition=_(""),
    )

    unspecified = Concept(
        prefLabel=_("Unspecified"),
        definition=_(""),
    )

    class Meta:
        name = "conductivity-methods"
        namespace = BASE_NAMESPACE + name + "/"
        prefix = "ghfdb"
        scheme_attrs = {
            "skos:prefLabel": _("Conductivity methods"),
            "skos:definition": _(
                "Methods used to calculate thermal conductivity in rock specimens or sections for the purpose of heat flow measurements."
            ),
        }
        collections = {
            "laboratory": Collection(
                prefLabel=_("Laboratory"),
                definition=_("Laboratory measurements"),
                members=[
                    "pointSource",
                    "lineSourceFull",
                    "lineSourceHalf",
                    "planeSourceFull",
                    "planeSourceHalf",
                    "laboratoryOther",
                ],
            ),
            "probe": Collection(
                prefLabel=_("Probe"),
                definition=_("Probe measurements"),
                members=[
                    "probePulse",
                ],
            ),
            "well_log": Collection(
                prefLabel=_("Well-log"),
                definition=_("Well-log interpretation"),
                members=[
                    "wellLogDeterministic",
                    "wellLogEmpirical",
                ],
            ),
            "estimation": Collection(
                prefLabel=_("Estimation"),
                definition=_("Estimation from other sources"),
                members=[
                    "chlorineContent",
                    "waterContent",
                    "lithology",
                    "mineralComposition",
                ],
            ),
            "other": Collection(
                prefLabel=_("Other"),
                definition=_("Other methods"),
                members=[
                    "unspecified",
                ],
            ),
        }


class ConductivityLocation(VocabularyBuilder):
    """Specification of the location where the thermal conductivity was measured."""

    actual = Concept(
        prefLabel=_("Actual heat-flow location"),
        definition=_(""),
    )

    other = Concept(
        prefLabel=_("Other location"),
        definition=_(""),
    )

    literature = Concept(
        prefLabel=_("Literature/unspecified"),
        definition=_(""),
    )

    class Meta:
        name = "conductivity-location"
        namespace = BASE_NAMESPACE + name + "/"
        prefix = "ghfdb"
        scheme_attrs = {
            "skos:prefLabel": _("Conductivity location"),
        }


class ConductivitySaturation(VocabularyBuilder):
    """
    Specification of the saturation state of the rocks during the thermal conductivity measurement.
    """

    saturatedInSitu = Concept(
        prefLabel=_("Saturated measured in-situ"),
        definition=_("Insitu saturated measured (measurements with probe sensing / marine measurements)"),
    )

    recovered = Concept(
        prefLabel=_("Recovered"),
        definition=_(
            "As recovered (rocks have been preserved and measured in close to their natural saturation state)."
        ),
    )

    saturatedMeasured = Concept(
        prefLabel=_("Saturated measured"),
        definition=_("Saturated measured (rocks have been technically saturated completely before measurement)."),
    )

    saturatedCalculated = Concept(
        prefLabel=_("Saturated calculated"),
        definition=_(
            "Thermal conductivity has been calculated from dry measured rocks, porosity and pore-filling fluid"
        ),
    )

    dryMeasured = Concept(
        prefLabel=_("Dry measured"),
        definition=_("Rocks have been technically dried before measurement"),
    )

    other = Concept(
        prefLabel=_("Other"),
        definition=_("Other saturation state (must be specified in comments)"),
    )

    unspecified = Concept(
        prefLabel=_("Unspecified"),
        definition=_(""),
    )

    class Meta:
        name = "conductivity-location"
        namespace = BASE_NAMESPACE + name + "/"
        prefix = "ghfdb"
        scheme_attrs = {
            "skos:prefLabel": _("Heat-flow specific conductivity saturation states"),
        }


class ConductivityPTConditions(VocabularyBuilder):
    """
    Specification of the conditions under which the thermal conductivity was measured.
    """

    unrecordedAmbient = Concept(
        prefLabel=_("Unrecorded ambient pT conditions"),
        definition=_(""),
    )

    recordedAmbient = Concept(
        prefLabel=_("Recorded ambient pT conditions"),
        definition=_(""),
    )

    actualInSitu = Concept(
        prefLabel=_("Actual in-situ (pT) conditions"),
        definition=_(""),
    )

    replicatedP = Concept(
        prefLabel=_("Replicated in-situ (p)"),
        definition=_(""),
    )

    replicatedT = Concept(
        prefLabel=_("Replicated in-situ (T)"),
        definition=_(""),
    )

    replicatedPT = Concept(
        prefLabel=_("Replicated in-situ (pT)"),
        definition=_(""),
    )

    correctedP = Concept(
        prefLabel=_("Corrected in-situ (p)"),
        definition=_(""),
    )

    correctedT = Concept(
        prefLabel=_("Corrected in-situ (T)"),
        definition=_(""),
    )

    correctedPT = Concept(
        prefLabel=_("Corrected in-situ (pT)"),
        definition=_(""),
    )

    unspecified = Concept(
        prefLabel=_("Unspecified"),
        definition=_(""),
    )

    class Meta:
        name = "conductivity-conditions"
        namespace = BASE_NAMESPACE + name + "/"
        prefix = "ghfdb"
        scheme_attrs = {
            "skos:prefLabel": _("Conductivity measurement conditions"),
            "skos:definition": _("Conditions under which the thermal conductivity was measured."),
        }
        collections = {
            "recorded": Collection(
                prefLabel=_("Recorded"),
                definition=_("Determinations under true conditions at target depths (e.g. sensing in boreholes)"),
                members=[
                    "recordedAmbient",
                ],
            ),
            "replicated": Collection(
                prefLabel=_("Replicated conditions"),
                definition=_(
                    "Determinations where the conditions at target depths are replicated under laboratory conditions"
                ),
                members=[
                    "replicatedP",
                    "replicatedT",
                    "replicatedPT",
                ],
            ),
            "corrected": Collection(
                prefLabel=_("Corrected conditions"),
                definition=_(
                    "Determinations under laboratory pT conditions that were corrected to conditions at target depths"
                ),
                members=[
                    "correctedP",
                    "correctedT",
                    "correctedPT",
                ],
            ),
            "actual": Collection(
                prefLabel=_("Actual"),
                definition=_("The condition at the respective depth of the heat-flow interval."),
                members=[
                    "actualInSitu",
                ],
            ),
        }


class ConductivityStrategy(VocabularyBuilder):
    """
    Specification of the strategy used to determine the thermal conductivity.
    """

    random = Concept(
        prefLabel=_("Random or periodic depth sampling (number)"),
        definition=_("Random or periodic depth sampling (number)"),
    )

    characterize = Concept(
        prefLabel=_("Characterize formation conductivities"),
        definition=_("Characterize formation conductivities"),
    )

    well_log = Concept(
        prefLabel=_("Well log interpretation"),
        definition=_("Well log interpretation"),
    )

    computation = Concept(
        prefLabel=_("Computation from probe sensing"),
        definition=_("Computation from probe sensing"),
    )

    other = Concept(
        prefLabel=_("Other"),
        definition=_("Other"),
    )

    unspecified = Concept(
        prefLabel=_("Unspecified"),
        definition=_("Unspecified"),
    )

    class Meta:
        name = "conductivity-strategy"
        prefix = "ghfdb"
        namespace = BASE_NAMESPACE + name + "/"
        scheme_attrs = {
            "skos:prefLabel": _("Thermal conductivity strategy"),
            "skos:definition": _(
                "Strategy by which thermal conductivity for a particular heat flow interval was calculated."
            ),
        }


class ConductivityPTFunction(VocabularyBuilder):
    """
    Specification of the function used to determine the thermal conductivity.
    """

    Tikhomirov1968 = Concept(
        prefLabel="T - Tikhomirov (1968)",
    )

    KutasGordienko1971 = Concept(
        prefLabel="Kutas & Gordienko (1971)",
    )

    Anand1973 = Concept(
        prefLabel="Anand et al. (1973)",
    )

    HaenelZoth1973 = Concept(
        prefLabel="Haenel & Zoth (1973)",
    )

    Blesch1983 = Concept(
        prefLabel="Blesch et al. (1983)",
    )

    Sekiguchi1984 = Concept(
        prefLabel="Sekiguchi (1984)",
    )

    Chapman1984 = Concept(
        prefLabel="Chapman et al. (1984)",
    )

    ZothHaenal1988 = Concept(
        prefLabel="Zoth & Haenel (1988)",
    )

    Somerton1992 = Concept(
        prefLabel="Somerton (1992)",
    )

    Sass1992 = Concept(
        prefLabel="Sass et al. (1992)",
    )

    Funnell1996 = Concept(
        prefLabel="Funnell et al. (1996)",
    )

    Kukkonen1999 = Concept(
        prefLabel="Kukkonen et al. (1999)",
    )

    Seipold2001 = Concept(
        prefLabel="Seipold (2001)",
    )

    VosteenSchellschmidt2003 = Concept(
        prefLabel="Vosteen & Schellschmidt (2003)",
    )

    Sun2017 = Concept(
        prefLabel="Sun et al. (2017)",
    )

    Miranda2018 = Concept(
        prefLabel="Miranda et al. (2018)",
    )

    Ratcliff1960 = Concept(
        prefLabel="Ratcliff (1960)",
    )

    Bridgman1924 = Concept(
        prefLabel="Bridgman (1924)",
    )

    Sibbitt1975 = Concept(
        prefLabel="Sibbitt (1975)",
    )

    Kukkonen1999 = Concept(
        prefLabel="Kukkonen et al. (1999)",
    )

    Seipold2001 = Concept(
        prefLabel="Seipold (2001)",
    )

    Duruturk2002 = Concept(
        prefLabel="Durutürk et al. (2002)",
    )

    Demirci2004 = Concept(
        prefLabel="Demirci et al. (2004)",
    )

    Gorgulu2008 = Concept(
        prefLabel="Görgülü et al. (2008)",
    )

    FuchsFoerster2014 = Concept(
        prefLabel="Fuchs & Förster (2014)",
    )

    Radcliff1960 = Concept(
        prefLabel="Radcliff (1960)",
    )

    Buntebarth1991 = Concept(
        prefLabel="Buntebarth (1991)",
    )

    ChapmanFurlong1992 = Concept(
        prefLabel="Chapman & Furlong (1992)",
    )

    Emirov1997 = Concept(
        prefLabel="Emirov et al. (1997)",
    )

    Abdulagatov2006 = Concept(
        prefLabel="Abdulagatov et al. (2006)",
    )

    EmirovRamazanova2007 = Concept(
        prefLabel="Emirov & Ramazanova (2007)",
    )

    Abdulagatova2009 = Concept(
        prefLabel="Abdulagatova et al. (2009)",
    )

    RamazanovaEmirov2010 = Concept(
        prefLabel="Ramazanova & Emirov (2010)",
    )

    RamazanovaEmirov2012 = Concept(
        prefLabel="Ramazanova & Emirov (2012)",
    )

    Emirov2017 = Concept(
        prefLabel="Emirov et al. (2017)",
    )

    site_specific = Concept(
        prefLabel=_("Site-specific experimental relationships"),
        definition=_(""),
    )

    other = Concept(
        prefLabel=_("Other"),
        definition=_(""),
    )

    unspecified = Concept(
        prefLabel=_("Unspecified"),
        definition=_(""),
    )

    class Meta:
        name = "conductivity-pt-function"
        prefix = "ghfdb"
        namespace = BASE_NAMESPACE + name + "/"
        scheme_attrs = {
            "skos:prefLabel": _("Thermal conductivity PT function"),
        }
        collections = {
            "temperature": Collection(
                prefLabel=_("Temperature"),
                definition=_(""),
                members=[
                    "Tikhomirov1968",
                    "KutasGordienko1971",
                    "Anand1973",
                    "HaenelZoth1973",
                    "Blesch1983",
                    "Sekiguchi1984",
                    "Chapman1984",
                    "ZothHaenal1988",
                    "Somerton1992",
                    "Sass1992",
                    "Funnell1996",
                    "Kukkonen1999",
                    "Seipold2001",
                    "VosteenSchellschmidt2003",
                    "Sun2017",
                    "Miranda2018",
                    "Ratcliff1960",
                ],
            ),
            "pressure": Collection(
                prefLabel=_("Pressure"),
                definition=_(""),
                members=[
                    "Bridgman1924",
                    "Sibbitt1975",
                    "Kukkonen1999",
                    "Seipold2001",
                    "Duruturk2002",
                    "Demirci2004",
                    "Gorgulu2008",
                    "FuchsFoerster2014",
                ],
            ),
            "pressure_temperature": Collection(
                prefLabel=_("Pressure and Temperature"),
                definition=_(""),
                members=[
                    "Radcliff1960",
                    "Buntebarth1991",
                    "ChapmanFurlong1992",
                    "Emirov1997",
                    "Abdulagatov2006",
                    "EmirovRamazanova2007",
                    "Abdulagatova2009",
                    "RamazanovaEmirov2010",
                    "RamazanovaEmirov2012",
                    "Emirov2017",
                ],
            ),
        }


class GenericFlagChoices(VocabularyBuilder):
    """Generic flag choices for heat flow data."""

    present_corrected = Concept(
        prefLabel=_("Present and corrected"),
        definition=_(""),
    )

    present_not_corrected = Concept(
        prefLabel=_("Present and not corrected"),
        definition=_(""),
    )

    present_not_significant = Concept(
        prefLabel=_("Present not significant"),
        definition=_(""),
    )

    not_recognized = Concept(
        prefLabel=_("not recognized"),
        definition=_(""),
    )

    consideredP = Concept(
        prefLabel=_("Considered - pressure"),
        definition=_(""),
    )

    consideredT = Concept(
        prefLabel=_("Considered - temperature"),
        definition=_(""),
    )

    consideredPT = Concept(
        prefLabel=_("Considered - pT"),
        definition=_(""),
    )

    notConsidered = Concept(
        prefLabel=_("Not considered"),
        definition=_(""),
    )

    tiltCorrected = Concept(
        prefLabel=_("Tilt corrected"),
        definition=_(""),
    )

    driftCorrected = Concept(
        prefLabel=_("Drift corrected"),
        definition=_(""),
    )

    notCorrected = Concept(
        prefLabel=_("Not corrected"),
        definition=_(""),
    )

    corrected = Concept(
        prefLabel=_("Corrected (specify)"),
        definition=_(""),
    )

    unspecified = Concept(
        prefLabel=_("unspecified"),
        definition=_(""),
    )

    class Meta:
        name = "heat-flow-corrections"
        prefix = "ghfdb"
        namespace = BASE_NAMESPACE + name + "/"
        scheme_attrs = {
            "skos:prefLabel": _("Generic flag choices"),
        }
        collections = {
            "generic": Collection(
                prefLabel=_("Generic"),
                definition=_("Generic flag choices for heat flow data"),
                members=[
                    "present_corrected",
                    "present_not_corrected",
                    "present_not_significant",
                    "unrecognized",
                    "unspecified",
                ],
            ),
            "insitu": Collection(
                prefLabel=_("In-situ"),
                definition=_("In-situ measurements"),
                members=[
                    "consideredP",
                    "consideredT",
                    "consideredPT",
                    "notConsidered",
                    "unspecified",
                ],
            ),
            "temperature": Collection(
                prefLabel=_("Temperature"),
                definition=_("Temperature measurements"),
                members=[
                    "tiltCorrected",
                    "driftCorrected",
                    "notCorrected",
                    "corrected",
                    "unspecified",
                ],
            ),
        }
