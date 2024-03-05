import random

import factory
from factory.fuzzy import FuzzyChoice
from geoluminate.factories import MeasurementFactory, randint

from . import vocabularies
from .models import HeatFlow, HeatFlowChild


class HeatFlowChildFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HeatFlowChild

    # parent = factory.RelatedFactory(
    #     "heat_flow.factories.HeatFlowFactory",
    #     factory_related_name="relevant_child",
    # )

    qc = factory.LazyAttribute(lambda _: round(random.gauss(mu=50, sigma=30), 2))
    qc_uncertainty = factory.LazyAttribute(lambda o: o.qc * random.uniform(0.05, 0.25))
    # qc_uncertainty = factory.Faker("pyfloat", min_value=0, max_value=10**6, right_digits=2)

    # metadata fields
    q_method = FuzzyChoice(vocabularies.HeatFlowMethod.values)
    q_top = factory.Faker("pyfloat", min_value=0, max_value=11999)
    q_bottom = factory.LazyAttribute(lambda o: random.uniform(o.q_top, 12000))
    expedition = factory.Faker("text", max_nb_chars=100)
    lithology = FuzzyChoice(vocabularies.SimpleLithology.values)
    stratigraphy = FuzzyChoice(vocabularies.ISC2020.values)
    relevant_child = FuzzyChoice([True, False, None])

    # probe fields
    probe_penetration = factory.Faker("pyfloat", min_value=0, max_value=1000)
    probe_type = FuzzyChoice(vocabularies.ProbeType.values)
    probe_length = factory.Faker("pyfloat", min_value=0, max_value=100)
    probe_tilt = factory.Faker("pyfloat", min_value=0, max_value=90)
    water_temperature = factory.Faker("pyfloat", min_value=-10, max_value=1000)

    # Temperature Fields
    T_grad_mean = factory.Faker("pyfloat", min_value=-(10**5), max_value=10**5)
    T_grad_uncertainty = factory.Faker("pyfloat", min_value=0, max_value=10**5)
    T_grad_mean_cor = factory.Faker("pyfloat", min_value=-(10**5), max_value=10**5)
    T_grad_uncertainty_cor = factory.Faker("pyfloat", min_value=0, max_value=10**5)
    T_method_top = FuzzyChoice(vocabularies.TemperatureMethod.values)
    T_method_bottom = FuzzyChoice(vocabularies.TemperatureMethod.values)
    T_shutin_top = factory.Faker("pyfloat", min_value=0, max_value=10000)
    T_shutin_bottom = factory.Faker("pyfloat", min_value=0, max_value=10000)
    T_correction_top = FuzzyChoice(vocabularies.TemperatureCorrection.values)
    T_correction_bottom = FuzzyChoice(vocabularies.TemperatureCorrection.values)
    T_number = factory.Faker("pyint", min_value=1, max_value=100)

    # Conductivity fields
    tc_mean = factory.Faker("pyfloat", min_value=0, max_value=100)
    tc_uncertainty = factory.Faker("pyfloat", min_value=0, max_value=100)
    tc_source = FuzzyChoice(vocabularies.ConductivitySource.values)
    tc_method = FuzzyChoice(vocabularies.ConductivityMethod.values)
    tc_saturation = FuzzyChoice(vocabularies.ConductivitySaturation.values)
    tc_pT_conditions = FuzzyChoice(vocabularies.ConductivityPTConditions.values)
    tc_pT_function = FuzzyChoice(vocabularies.ConductivityPTFunction, getter=lambda c: c[0])
    tc_strategy = FuzzyChoice(vocabularies.ConductivityStrategy.values)
    tc_number = factory.Faker("pyint", min_value=1, max_value=10000)

    # correction fields
    corr_IS_flag = FuzzyChoice(vocabularies.InSituFlagChoices.values)
    corr_T_flag = FuzzyChoice(vocabularies.TemperatureFlagChoices.values)
    corr_S_flag = FuzzyChoice(vocabularies.GenericFlagChoices.values)
    corr_E_flag = FuzzyChoice(vocabularies.GenericFlagChoices.values)
    corr_TOPO_flag = FuzzyChoice(vocabularies.GenericFlagChoices.values)
    corr_PAL_flag = FuzzyChoice(vocabularies.GenericFlagChoices.values)
    corr_SUR_flag = FuzzyChoice(vocabularies.GenericFlagChoices.values)
    corr_CONV_flag = FuzzyChoice(vocabularies.GenericFlagChoices.values)
    corr_HR_flag = FuzzyChoice(vocabularies.GenericFlagChoices.values)


class HeatFlowFactory(MeasurementFactory):
    class Meta:
        model = HeatFlow

    q = factory.Faker("pyfloat", min_value=-10, max_value=150)
    q_uncertainty = factory.Faker("pyfloat", min_value=0, max_value=100)
    environment = FuzzyChoice(vocabularies.GeographicEnvironment.values)
    corr_HP_flag = FuzzyChoice([True, False, None])
    total_depth_MD = factory.Faker("pyfloat", min_value=-12000, max_value=9000)
    total_depth_TVD = factory.Faker("pyfloat", min_value=-12000, max_value=9000)
    explo_method = FuzzyChoice(vocabularies.ExplorationMethod.values)
    explo_purpose = FuzzyChoice(vocabularies.ExplorationPurpose.values)
    children = factory.RelatedFactoryList(
        "heat_flow.factories.HeatFlowChildFactory",
        parent=None,
        factory_related_name="parent",
        size=randint(1, 5),
    )
