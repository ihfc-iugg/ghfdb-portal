import random

import factory
from earth_science.factories.location import BoreholeFactory, GeoDepthIntervalFactory
from factory.fuzzy import FuzzyChoice
from geoluminate.factories import MeasurementFactory

from .models import (
    # ChildConductivity,
    ChildHeatFlow,
    HeatFlowInterval,
    HeatFlowSite,
    ParentHeatFlow,
)


class HeatFlowSiteFactory(BoreholeFactory):
    environment = FuzzyChoice(HeatFlowSite.environment_vocab.values)
    explo_method = FuzzyChoice(HeatFlowSite.explo_method_vocab.values)
    explo_purpose = FuzzyChoice(HeatFlowSite.explo_purpose_vocab.values)

    class Meta:
        model = HeatFlowSite


class HeatFlowIntervalFactory(GeoDepthIntervalFactory):
    class Meta:
        model = HeatFlowInterval


class ParentHeatFlowFactory(MeasurementFactory):
    class Meta:
        model = ParentHeatFlow

    value = factory.LazyAttribute(lambda _: round(random.gauss(mu=50, sigma=30), 2))
    uncertainty = factory.LazyAttribute(lambda o: o.value * random.uniform(0.05, 0.25))  # noqa: S311
    corr_HP_flag = FuzzyChoice([True, False, None])
    is_ghfdb = factory.Faker("boolean", chance_of_getting_true=0.9)
    # children = factory.RelatedFactoryList(
    #     "heat_flow.factories.ChildHeatFlowFactory",
    #     parent=None,
    #     factory_related_name="parent",
    #     size=randint(1, 5),
    # )


class ChildHeatFlowFactory(MeasurementFactory):
    class Meta:
        model = ChildHeatFlow

    # parent = factory.RelatedFactory(
    #     "heat_flow.factories.HeatFlowFactory",
    #     factory_related_name="relevant_child",
    # )

    value = factory.LazyAttribute(lambda _: round(random.gauss(mu=50, sigma=30), 2))
    uncertainty = factory.LazyAttribute(lambda o: o.value * random.uniform(0.05, 0.25))  # noqa: S311

    # metadata fields
    method = FuzzyChoice(ChildHeatFlow.method_vocab.values)
    expedition = factory.Faker("text", max_nb_chars=100)
    relevant_child = factory.Faker("boolean", chance_of_getting_true=0.8)

    # probe fields
    # length = factory.LazyAttribute(lambda o: random.uniform(0, o.probe_length))
    probe_penetration = factory.Faker("pyfloat", min_value=0, max_value=1000)
    probe_type = FuzzyChoice(ChildHeatFlow.probe_type_vocab.values)
    probe_length = factory.Faker("pyfloat", min_value=0, max_value=100)
    probe_tilt = factory.Faker("pyfloat", min_value=0, max_value=90)
    water_temperature = factory.Faker("pyfloat", min_value=-10, max_value=1000)

    # temperature_gradient = factory.SubFactory("heat_flow.factories.TemperatureGradientFactory")
    # thermal_conductivity = factory.SubFactory("heat_flow.factories.ChildConductivityFactory")

    # correction fields
    corr_IS_flag = FuzzyChoice(ChildHeatFlow.corr_IS_flag_vocab.values)
    corr_T_flag = FuzzyChoice(ChildHeatFlow.corr_IS_flag_vocab.values)
    corr_S_flag = FuzzyChoice(ChildHeatFlow.corr_IS_flag_vocab.values)
    corr_E_flag = FuzzyChoice(ChildHeatFlow.corr_IS_flag_vocab.values)
    corr_TOPO_flag = FuzzyChoice(ChildHeatFlow.corr_IS_flag_vocab.values)
    corr_PAL_flag = FuzzyChoice(ChildHeatFlow.corr_IS_flag_vocab.values)
    corr_SUR_flag = FuzzyChoice(ChildHeatFlow.corr_IS_flag_vocab.values)
    corr_CONV_flag = FuzzyChoice(ChildHeatFlow.corr_IS_flag_vocab.values)
    corr_HR_flag = FuzzyChoice(ChildHeatFlow.corr_IS_flag_vocab.values)


# class TemperatureGradientFactory(MeasurementFactory):
#     class Meta:
#         model = "heat_flow.TemperatureGradient"

#     mean = factory.Faker("pyfloat", min_value=-(10**5), max_value=10**5)
#     uncertainty = factory.Faker("pyfloat", min_value=0, max_value=10**5)
#     corrected_mean = factory.Faker("pyfloat", min_value=-(10**5), max_value=10**5)
#     corrected_uncertainty = factory.Faker("pyfloat", min_value=0, max_value=10**5)
#     method_top = FuzzyChoice(TemperatureGradient.method_top_vocab.values)
#     method_bottom = FuzzyChoice(TemperatureGradient.method_bottom_vocab.values)
#     shutin_top = factory.Faker("pyfloat", min_value=0, max_value=10000)
#     shutin_bottom = factory.Faker("pyfloat", min_value=0, max_value=10000)
#     correction_top = FuzzyChoice(TemperatureGradient.correction_top_vocab.values)
#     correction_bottom = FuzzyChoice(TemperatureGradient.correction_bottom_vocab.values)
#     number = factory.Faker("pyint", min_value=1, max_value=100)


# class ChildConductivityFactory(DjangoModelFactory):
#     class Meta:
#         model = "heat_flow.ChildConductivity"

#     mean = factory.Faker("pyfloat", min_value=0, max_value=100)
#     uncertainty = factory.Faker("pyfloat", min_value=0, max_value=100)
#     source = FuzzyChoice(ChildConductivity.source_vocab.values)
#     method = FuzzyChoice(ChildConductivity.method_vocab.values)
#     saturation = FuzzyChoice(ChildConductivity.saturation_vocab.values)
#     pT_conditions = FuzzyChoice(ChildConductivity.pT_conditions_vocab.values)
#     pT_function = FuzzyChoice(ChildConductivity.pT_function_vocab, getter=lambda c: c[0])
#     strategy = FuzzyChoice(ChildConductivity.strategy_vocab.values)
#     number = factory.Faker("pyint", min_value=1, max_value=10000)
