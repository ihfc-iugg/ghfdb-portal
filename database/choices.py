from typing import Mapping
from django.db import models
from django.utils.translation import gettext as _

"""These are the old static choice fields before moving to dynamic model based fields"""


class ConductivitySource(models.TextChoices):
    OUTCROP = 'outcrop samples', _('Outcrop samples')
    CORE = 'core samples', _('Core samples')
    CUTTINGS = 'cutting samples', _('Cutting samples')
    MINERAL_COMP = 'mineral computation', _('Mineral computation')
    WELL_LOG_INTERP = 'well log interpretation', _('Well log interpretation')
    CORE_LOG_INT = 'core-log integration', _('Core-log integration')
    IN_SITU_PROBE = 'in-situ probe', _('In-situ probe')
    OTHER = 'other', _('Other (specify in comments field)')
    NOT_SPECIFIED = 'unspecified', _('Unspecified')

class CorrectionType(models.TextChoices):
    BWT = 'BWT', _('Bottom water temperature variation')
    CONV = 'CONV', _('Convection processes')
    E = 'E', _('Erosion')
    IS = 'IS', _('In-situ thermal properties')
    HP = 'HP', _('Heat production')
    HR = 'HR', _('Heat refraction')
    S = 'S', _('Sedimentation')
    T = 'T', _('Temperature')
    PAL = 'PAL', _('Transient climatic')
    TOPO = 'TOPO', _('Topographic')

class ExplorationPurpose(models.TextChoices):

    HYDROCARBON = 'hydrocarbon', _('Hydrocarbon')
    STORAGE = 'underground storage', _('Underground Storage')
    GEOTHERMAL = 'geothermal', _('Geothermal')
    MAPPING = 'mapping', _('Mapping')
    MINING = 'mining', _('Mining')
    TUNNELING = 'tunneling', _('Tunneling')
    UNSPEC = 'unspecified', _('Unspecified')

class ExplorationMethod(models.TextChoices):
    DRILLING = 'drilling', _('Drilling')
    MINING = 'mining', _('Mining')
    TUNNELING = 'tunneling', _('Tunneling')
    PROBE_LAKE = 'probing (lake)', _('Probing (Lake)')
    PROBE_OCEAN = 'probing (ocean)', _('Probing (Ocean)')
    UNSPEC = 'unspecified', _('Unspecified')

class GeographicEnvironment(models.TextChoices):
    ONSHORE_CONT = 'onshore (continental)', _('Onshore (Continental)')
    ONSHORE_LAKE = 'onshore (lake)', _('Onshore (Lake)')
    OFFSHORE_CONT = 'offshore (continental)', _('Offshore (Continental)')
    OFFSHORE_MARINE = 'offshore (marine)', _('Offshore (Marine)')
    UNSPEC = 'unspecified', _('Unspecified')

class HeatFlowMethod(models.TextChoices):
    FOURIER = 'fourier', _("Fourier's Law")
    PRODUCT = 'product', _("Product method")
    INTERVAL = 'interval', _("Interval method")
    BULLARD = 'bullard', _("Bullard")
    BOOTSTRAP = 'bootsrap', _("Bootstrap")

class HeatTransfer(models.TextChoices):
    COND = 'conductive', _('Conductive')
    CONVEC_UNSPEC = 'convective unspecified', _('Convective - unspecified')
    CONVEC_UP = 'convective upflow', _('Convective - upflow')
    CONVEC_DOWN = 'convective downflow', _('Convective - downflow')
    UNSPEC = 'unspecified', _('Unspecified')

class ProbeType(models.TextChoices):
    CORER = 'corer-outrigger', _('Corer-outrigger')
    BULLARD = 'bullard', _('Bullard Probe')
    LISTER = 'lister/violin', _('Lister Violin-Bow Probe')
    EWING = 'ewing', _('Ewing Probe')
    OTHER = 'other', _('Other')
    UNSPEC = 'unspecified', _('Unspecified')

class TC_PT_Conditions(models.TextChoices):
    UNRECORDED = 'unrecorded ambient pt conditions', _('Unrecorded ambient pT conditions')
    RECORDED = 'recorded ambient pt conditions', _('Recorded ambient pT conditions')
    REPLICATED_P = 'replicated in-situ (p)', _('Replicated in-situ (p)')
    REPLICATED_T = 'replicated in-situ (t)', _('Replicated in-situ (T)')
    REPLICATED = 'replicated in-situ (pt)', _('Replicated in-situ (pT)')
    ACTUAL = 'actual in-situ (pt) conditions', _('Actual in-situ (pT) conditions')

class TC_SaturationMethod(models.TextChoices):
    DRY_MEAS = 'drymeas', _('Dry measured (rocks have been technically dried before measurement)')
    SAT_MEAS = 'satmeas', _('Saturated measured (rocks have been technically saturated completely before measurement)')
    INSITU_SAT_MEAS = 'insitusatmeas', _(' Insitu saturated measured (measurements with probe sensing / marine measurements)')
    CORE_SAT = 'coresatmeas', _('saturated measured on closed sediment cores on-board')
    SAT_CALC = 'satcalc', _('Saturated calculated (thermal conductivity has been calculated from dry measured rocks, porosity and pore-filling fluid)')
    RECOV = 'recov', _('As recovered (rocks have been preserved and measured in close to their natural saturation state)')
    OTHER = 'other', _('Other')
    UNSPECIFIED = 'unspecified', _('Unspecified')
    NA = 'n/a', _('N/A')

class TempMethod(models.TextChoices):
    BHT = 'bht', _('Bottom hole temperature (uncorrected)')
    CBHT = 'cbht', _('Bottom hole temperature (corrected)')
    DST = 'dst', _('Drill stem test')
    PT1000 = 'pt100', _('Pt-100 probe')
    PT10000 = 'pt1000', _('Pt-1000 probe')
    LOG = 'log', _('Continuous temperature log')
    CLOG = 'clog', _('Corrected temperature log')
    DTS = 'dts', _('Distributed temperature sensing')
    CPD = 'cpd', _('Cure point depth estimate')
    XEN = 'xen', _('Xenlith')
    GTM = 'gtm', _('Geothermometry')
    BSR = 'bsr', _('Bottom-simulating seismic reflector')
    APCT = 'apct/set-2', _('Ocean drilling temperature tool')
    SUR = 'sur', _('Surface temperature')

class TempCorrectionMethod(models.TextChoices):
    HORNER = 'hp', _('Horner Plot')
    CSM = 'csm', _('Cylinder source method')
    LSM = 'lsm', _('Line source explosion method')
    IM = 'im', _('Inverse numerical modelling')
    OTHER = 'other', _('Other')
    NOT_CORRECTED = 'not corrected', _('Not corrected')
    UNSPECIFIED = 'unspecified', _('Unspecified')
