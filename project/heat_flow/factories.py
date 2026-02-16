import random

from factory.declarations import LazyAttribute
from factory.faker import Faker
from factory.fuzzy import FuzzyChoice
from fairdm.factories import MeasurementFactory, SampleFactory

from .models import (
    HeatFlow,
    HeatFlowInterval,
    HeatFlowSite,
    IntervalConductivity,
    ThermalGradient,
)


class HeatFlowSiteFactory(SampleFactory):
    environment = FuzzyChoice(HeatFlowSite.environment_vocab.values)
    explo_method = FuzzyChoice(HeatFlowSite.explo_method_vocab.values)
    # Skip explo_purpose for now since it's a many-to-many field
    # explo_purpose = FuzzyChoice(get_vocabulary_choices(vocabularies.ExplorationPurpose))

    class Meta:
        model = HeatFlowSite


class HeatFlowIntervalFactory(SampleFactory):
    class Meta:
        model = HeatFlowInterval


class HeatFlowFactory(MeasurementFactory):
    class Meta:
        model = HeatFlow

    value = LazyAttribute(lambda _: round(random.gauss(mu=50, sigma=30), 2))
    uncertainty = LazyAttribute(lambda o: o.value * random.uniform(0.05, 0.25))  # noqa: S311

    # metadata fields
    # method = FuzzyChoice(HeatFlow.method_vocab.choices)  # ConceptManyToManyField
    expedition = Faker("text", max_nb_chars=100)

    # probe fields
    # length = LazyAttribute(lambda o: random.uniform(0, o.probe_length))
    probe_penetration = Faker("pyfloat", min_value=0, max_value=1000)
    # probe_type = FuzzyChoice(vocabularies.ProbeType.choices)  # ConceptManyToManyField
    probe_length = Faker("pyfloat", min_value=0, max_value=100)
    probe_tilt = Faker("pyfloat", min_value=0, max_value=90)
    water_temperature = Faker("pyfloat", min_value=-10, max_value=1000)

    # temperature_gradient = factory.SubFactory("heat_flow.factories.TemperatureGradientFactory")
    # thermal_conductivity = factory.SubFactory("heat_flow.factories.ChildConductivityFactory")

    # correction fields - Only corr_IS_flag and corr_T_flag are ConceptManyToManyField
    # corr_IS_flag = FuzzyChoice(HeatFlow.corr_IS_flag_vocab.choices)  # ConceptManyToManyField
    # corr_T_flag = FuzzyChoice(HeatFlow.corr_T_flag_vocab.choices)  # ConceptManyToManyField
    corr_S_flag = FuzzyChoice(HeatFlow.corr_S_flag_vocab.values)
    corr_E_flag = FuzzyChoice(HeatFlow.corr_E_flag_vocab.values)
    corr_TOPO_flag = FuzzyChoice(HeatFlow.corr_TOPO_flag_vocab.values)
    corr_PAL_flag = FuzzyChoice(HeatFlow.corr_PAL_flag_vocab.values)
    corr_SUR_flag = FuzzyChoice(HeatFlow.corr_SUR_flag_vocab.values)
    corr_CONV_flag = FuzzyChoice(HeatFlow.corr_CONV_flag_vocab.values)
    corr_HR_flag = FuzzyChoice(HeatFlow.corr_HR_flag_vocab.values)


class ThermalGradientFactory(MeasurementFactory):
    class Meta:
        model = ThermalGradient

    value = LazyAttribute(lambda _: round(random.gauss(mu=25, sigma=10), 2))
    uncertainty = LazyAttribute(lambda o: o.value * random.uniform(0.05, 0.25))  # noqa: S311
    corrected_value = LazyAttribute(lambda _: round(random.gauss(mu=25, sigma=10), 2))
    corrected_uncertainty = LazyAttribute(
        lambda o: o.corrected_value * random.uniform(0.05, 0.25) if o.corrected_value else None
    )
    # method_top = FuzzyChoice(vocabularies.TemperatureMethod.choices)  # ConceptManyToManyField
    # method_bottom = FuzzyChoice(vocabularies.TemperatureMethod.choices)  # ConceptManyToManyField
    shutin_top = Faker("pyint", min_value=0, max_value=10000)
    shutin_bottom = Faker("pyint", min_value=0, max_value=10000)
    # correction_top = FuzzyChoice(vocabularies.TemperatureCorrection.choices)  # ConceptManyToManyField
    # correction_bottom = FuzzyChoice(vocabularies.TemperatureCorrection.choices)  # ConceptManyToManyField
    number = Faker("pyint", min_value=1, max_value=100)
    score = Faker("pyfloat", min_value=0.0, max_value=1.0)


class IntervalConductivityFactory(MeasurementFactory):
    class Meta:
        model = IntervalConductivity

    value = LazyAttribute(lambda _: round(random.gauss(mu=2.5, sigma=1.0), 2))
    uncertainty = LazyAttribute(lambda o: o.value * random.uniform(0.05, 0.25))  # noqa: S311
    # source = FuzzyChoice(vocabularies.ConductivitySource.choices)  # ConceptManyToManyField
    # location = FuzzyChoice(vocabularies.ConductivityLocation.choices)  # ConceptManyToManyField
    # method = FuzzyChoice(vocabularies.ConductivityMethod.choices)  # ConceptManyToManyField
    # saturation = FuzzyChoice(vocabularies.ConductivitySaturation.choices)  # ConceptManyToManyField
    # pT_conditions = FuzzyChoice(vocabularies.ConductivityPTConditions.choices)  # ConceptManyToManyField
    # pT_function = FuzzyChoice(vocabularies.ConductivityPTFunction.choices)  # ConceptManyToManyField
    # strategy = FuzzyChoice(vocabularies.ConductivityStrategy.choices)  # ConceptManyToManyField
    number = Faker("pyint", min_value=1, max_value=10000)
