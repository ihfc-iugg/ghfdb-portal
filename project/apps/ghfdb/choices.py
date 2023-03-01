from django.db import models
from django.utils.translation import gettext as _


class CorrectionApplied(models.TextChoices):
    YES = 'yes', _('Yes')
    NO = 'no', _('No')
    MENTIONED = 'mentioned', _('Mentioned in-text but unclear if applied')


class TypeChoices(models.TextChoices):
    CON_PT = 'tc_pT_conditions', _('TC PT Conditions')
    CON_SAT = 'tc_saturation', _('TC Saturation State')
    CON_SRC = 'tc_source', _('TC Source')
    CORR = 'corrections', _('Correction')
    ENV = 'environment', _('Environment')
    EX_METH = 'explo_method', _('Exploration Method')
    EX_PUR = 'explo_purpose', _('Exploration Purpose')
    HF_METH = 'q_method', _('Heat Flow Method')
    PROBE = 'hf_probe', _('Probe Type')
    TMP_COR = 'T_correction_method', _('Temp. Corr. Method')
    TMP_METH = 'T_method', _('Temp. Method')
    TRA_MEC = 'q_tf_mechanism', _('Transfer Mechanism')
