# import tzinfo from datetime
import datetime
import random

import factory
from factory.fuzzy import FuzzyChoice
from geoluminate.contrib.core.tests.factories import MeasurementFactory

from . import choices
from .models import HeatFlow, HeatFlowChild


class HeatFlowChildFactory(factory.Factory):
    class Meta:
        model = HeatFlowChild

    # parent = factory.Iterator(HeatFlow.objects.all())

    # parent = factory.RelatedFactory(
    #     HeatFlowFactory,
    #     factory_related_name="relevant_child",
    # )

    qc = factory.Faker("pyfloat", min_value=-(10**6), max_value=10**6)
    qc_uncertainty = factory.Faker("pyfloat", min_value=0, max_value=10**6)

    # metadata fields
    q_method = FuzzyChoice(choices.HeatFlowMethod.values)
    q_top = factory.Faker("pyfloat", min_value=0, max_value=12000)
    q_bottom = factory.Faker("pyfloat", min_value=0, max_value=12000)
    expedition = factory.Faker("text", max_nb_chars=100)
    relevant_child = FuzzyChoice([True, False, None])

    # probe fields
    probe_penetration = factory.Faker("pyfloat", min_value=0, max_value=1000)
    probe_type = FuzzyChoice(choices.ProbeType.values)
    probe_length = factory.Faker("pyfloat", min_value=0, max_value=100)
    probe_tilt = factory.Faker("pyfloat", min_value=0, max_value=90)
    water_temperature = factory.Faker("pyfloat", min_value=-10, max_value=1000)

    # Temperature Fields
    T_grad_mean = factory.Faker("pyfloat", min_value=-(10**5), max_value=10**5)
    T_grad_uncertainty = factory.Faker("pyfloat", min_value=0, max_value=10**5)
    T_grad_mean_cor = factory.Faker("pyfloat", min_value=-(10**5), max_value=10**5)
    T_grad_uncertainty_cor = factory.Faker("pyfloat", min_value=0, max_value=10**5)
    T_method_top = FuzzyChoice(choices.TemperatureMethod.values)
    T_method_bottom = FuzzyChoice(choices.TemperatureMethod.values)
    T_shutin_top = factory.Faker("pyfloat", min_value=0, max_value=10000)
    T_shutin_bottom = factory.Faker("pyfloat", min_value=0, max_value=10000)
    T_correction_top = FuzzyChoice(choices.TemperatureCorrection.values)
    T_correction_bottom = FuzzyChoice(choices.TemperatureCorrection.values)
    T_number = factory.Faker("pyint", min_value=1, max_value=100)

    # Conductivity fields
    tc_mean = factory.Faker("pyfloat", min_value=0, max_value=100)
    tc_uncertainty = factory.Faker("pyfloat", min_value=0, max_value=100)
    tc_source = FuzzyChoice(choices.ConductivitySource.values)
    tc_method = FuzzyChoice(choices.ConductivityMethod.values)
    tc_saturation = FuzzyChoice(choices.ConductivitySaturation.values)
    tc_pT_conditions = FuzzyChoice(choices.ConductivityPTConditions.values)
    tc_pT_function = FuzzyChoice(choices.ConductivityPTFunction, getter=lambda c: c[0])
    tc_strategy = FuzzyChoice(choices.ConductivityStrategy.values)
    tc_number = factory.Faker("pyint", min_value=1, max_value=10000)

    # correction fields
    corr_IS_flag = FuzzyChoice(choices.InSituFlagChoices.values)
    corr_T_flag = FuzzyChoice(choices.TemperatureFlagChoices.values)
    corr_S_flag = FuzzyChoice(choices.GenericFlagChoices.values)
    corr_E_flag = FuzzyChoice(choices.GenericFlagChoices.values)
    corr_TOPO_flag = FuzzyChoice(choices.GenericFlagChoices.values)
    corr_PAL_flag = FuzzyChoice(choices.GenericFlagChoices.values)
    corr_SUR_flag = FuzzyChoice(choices.GenericFlagChoices.values)
    corr_CONV_flag = FuzzyChoice(choices.GenericFlagChoices.values)
    corr_HR_flag = FuzzyChoice(choices.GenericFlagChoices.values)


class HeatFlowFactory(MeasurementFactory):
    class Meta:
        model = HeatFlow

    q = factory.Faker("pyfloat", min_value=-10, max_value=150)
    q_uncertainty = factory.Faker("pyfloat", min_value=0, max_value=100)
    environment = FuzzyChoice(choices.GeographicEnvironment.values)
    corr_HP_flag = FuzzyChoice([True, False, None])
    total_depth_MD = factory.Faker("pyfloat", min_value=-12000, max_value=9000)
    total_depth_TVD = factory.Faker("pyfloat", min_value=-12000, max_value=9000)
    explo_method = FuzzyChoice(choices.ExplorationMethod.values)
    explo_purpose = FuzzyChoice(choices.ExplorationPurpose.values)

    children = factory.RelatedFactoryList(HeatFlowChildFactory, size=lambda: random.randint(1, 5))
