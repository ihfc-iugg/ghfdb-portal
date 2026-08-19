import random

import factory
from factory.declarations import LazyAttribute
from factory.faker import Faker
from factory.fuzzy import FuzzyChoice
from fairdm.factories import MeasurementFactory, SampleFactory

from .models import (
    HeatFlow,
    HeatFlowInterval,
    HeatFlowSite,
    IntervalConductivity,
    ParentHeatFlow,
    ProbeMetadata,
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
    site = factory.SubFactory(HeatFlowSiteFactory)

    class Meta:
        model = HeatFlowInterval


class HeatFlowFactory(MeasurementFactory):
    class Meta:
        model = HeatFlow

    sample = factory.SubFactory(HeatFlowIntervalFactory)
    value = LazyAttribute(lambda _: round(random.gauss(mu=50, sigma=30), 2))
    uncertainty = LazyAttribute(lambda o: o.value * random.uniform(0.05, 0.25))

    # metadata fields
    # method = FuzzyChoice(HeatFlow.method_vocab.choices)  # ConceptManyToManyField
    expedition = Faker("text", max_nb_chars=100)

    # temperature_gradient = factory.SubFactory("heat_flow.factories.TemperatureGradientFactory")
    # thermal_conductivity = factory.SubFactory("heat_flow.factories.ChildConductivityFactory")


class ThermalGradientFactory(MeasurementFactory):
    class Meta:
        model = ThermalGradient

    sample = factory.SubFactory(HeatFlowIntervalFactory)

    value = LazyAttribute(lambda _: round(random.gauss(mu=25, sigma=10), 2))
    uncertainty = LazyAttribute(lambda o: o.value * random.uniform(0.05, 0.25))
    corrected_value = LazyAttribute(lambda _: round(random.gauss(mu=25, sigma=10), 2))
    corrected_uncertainty = LazyAttribute(
        lambda o: (
            o.corrected_value * random.uniform(0.05, 0.25)
            if o.corrected_value
            else None
        )
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

    sample = factory.SubFactory(HeatFlowIntervalFactory)

    value = LazyAttribute(lambda _: round(random.gauss(mu=2.5, sigma=1.0), 2))
    uncertainty = LazyAttribute(lambda o: o.value * random.uniform(0.05, 0.25))
    # source = FuzzyChoice(vocabularies.ConductivitySource.choices)  # ConceptManyToManyField
    # location = FuzzyChoice(vocabularies.ConductivityLocation.choices)  # ConceptManyToManyField
    # method = FuzzyChoice(vocabularies.ConductivityMethod.choices)  # ConceptManyToManyField
    # saturation = FuzzyChoice(vocabularies.ConductivitySaturation.choices)  # ConceptManyToManyField
    # pT_conditions = FuzzyChoice(vocabularies.ConductivityPTConditions.choices)  # ConceptManyToManyField
    # pT_function = FuzzyChoice(vocabularies.ConductivityPTFunction.choices)  # ConceptManyToManyField
    # strategy = FuzzyChoice(vocabularies.ConductivityStrategy.choices)  # ConceptManyToManyField
    number = Faker("pyint", min_value=1, max_value=10000)


class ParentHeatFlowFactory(MeasurementFactory):
    """Factory for ParentHeatFlow.  sample is a HeatFlowSite (one SubFactory level per R10)."""

    sample = factory.SubFactory(HeatFlowSiteFactory)

    class Meta:
        model = ParentHeatFlow

    value = LazyAttribute(lambda _: round(random.gauss(mu=50, sigma=20), 2))


class ProbeMetadataFactory(factory.django.DjangoModelFactory):
    """Factory for ProbeMetadata.  Requires an interval (depth-1 SubFactory acceptable per R10)."""

    interval = factory.SubFactory(HeatFlowIntervalFactory)
    penetration = Faker("pyfloat", min_value=0.1, max_value=10.0)
    length = Faker("pyfloat", min_value=1.0, max_value=10.0)
    tilt = Faker("pyfloat", min_value=0.0, max_value=45.0)

    class Meta:
        model = ProbeMetadata
