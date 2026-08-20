import random

import factory
from factory.declarations import LazyAttribute
from factory.faker import Faker
from factory.fuzzy import FuzzyChoice
from fairdm.factories import MeasurementFactory, SampleFactory
from research_vocabs.models import Concept

from heat_flow import vocabularies

from .models import (
    HeatFlow,
    HeatFlowCorrection,
    HeatFlowInterval,
    HeatFlowSite,
    IntervalConductivity,
    ParentHeatFlow,
    ProbeMetadata,
    ThermalGradient,
)


def attach_random_concept(instance, field_name, vocabulary):
    """Attach one concept drawn from *vocabulary* to *instance*'s *field_name*
    many-to-many field (R2, FR-036). Requires ``Concept.preload()`` to have run
    for the vocabulary's concepts to exist.
    """
    concepts = list(Concept.get_for_vocabulary(vocabulary))
    getattr(instance, field_name).set([random.choice(concepts)])


class HeatFlowSiteFactory(SampleFactory):
    environment = FuzzyChoice(HeatFlowSite.environment_vocab.values)
    explo_method = FuzzyChoice(HeatFlowSite.explo_method_vocab.values)

    class Meta:
        model = HeatFlowSite

    @factory.post_generation
    def explo_purpose(obj, create, extracted, **kwargs):
        """Attach an exploration-purpose concept (ConceptManyToManyField; FR-036)."""
        if not create:
            return
        if extracted is not None:
            obj.explo_purpose.set(extracted)
            return
        attach_random_concept(obj, "explo_purpose", vocabularies.ExplorationPurpose)


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
    expedition = Faker("text", max_nb_chars=100)

    @factory.post_generation
    def method(obj, create, extracted, **kwargs):
        """Attach a heat-flow-method concept (ConceptManyToManyField; FR-036)."""
        if not create:
            return
        if extracted is not None:
            obj.method.set(extracted)
            return
        attach_random_concept(obj, "method", vocabularies.HeatFlowMethod)


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
    shutin_top = Faker("pyint", min_value=0, max_value=10000)
    shutin_bottom = Faker("pyint", min_value=0, max_value=10000)
    number = Faker("pyint", min_value=1, max_value=100)
    score = Faker("pyfloat", min_value=0.0, max_value=1.0)

    @factory.post_generation
    def method_top(obj, create, extracted, **kwargs):
        """Attach a temperature-method concept for the interval top (FR-036)."""
        if not create:
            return
        if extracted is not None:
            obj.method_top.set(extracted)
            return
        attach_random_concept(obj, "method_top", vocabularies.TemperatureMethod)

    @factory.post_generation
    def method_bottom(obj, create, extracted, **kwargs):
        """Attach a temperature-method concept for the interval bottom (FR-036)."""
        if not create:
            return
        if extracted is not None:
            obj.method_bottom.set(extracted)
            return
        attach_random_concept(obj, "method_bottom", vocabularies.TemperatureMethod)

    @factory.post_generation
    def correction_top(obj, create, extracted, **kwargs):
        """Attach a temperature-correction concept for the interval top (FR-036)."""
        if not create:
            return
        if extracted is not None:
            obj.correction_top.set(extracted)
            return
        attach_random_concept(obj, "correction_top", vocabularies.TemperatureCorrection)

    @factory.post_generation
    def correction_bottom(obj, create, extracted, **kwargs):
        """Attach a temperature-correction concept for the interval bottom (FR-036)."""
        if not create:
            return
        if extracted is not None:
            obj.correction_bottom.set(extracted)
            return
        attach_random_concept(
            obj, "correction_bottom", vocabularies.TemperatureCorrection
        )


class IntervalConductivityFactory(MeasurementFactory):
    class Meta:
        model = IntervalConductivity

    sample = factory.SubFactory(HeatFlowIntervalFactory)

    value = LazyAttribute(lambda _: round(random.gauss(mu=2.5, sigma=1.0), 2))
    uncertainty = LazyAttribute(lambda o: o.value * random.uniform(0.05, 0.25))
    number = Faker("pyint", min_value=1, max_value=10000)

    @factory.post_generation
    def source(obj, create, extracted, **kwargs):
        """Attach a conductivity-source concept (FR-036)."""
        if not create:
            return
        if extracted is not None:
            obj.source.set(extracted)
            return
        attach_random_concept(obj, "source", vocabularies.ConductivitySource)

    @factory.post_generation
    def location(obj, create, extracted, **kwargs):
        """Attach a conductivity-location concept (FR-036)."""
        if not create:
            return
        if extracted is not None:
            obj.location.set(extracted)
            return
        attach_random_concept(obj, "location", vocabularies.ConductivityLocation)

    @factory.post_generation
    def method(obj, create, extracted, **kwargs):
        """Attach a conductivity-method concept (FR-036)."""
        if not create:
            return
        if extracted is not None:
            obj.method.set(extracted)
            return
        attach_random_concept(obj, "method", vocabularies.ConductivityMethod)

    @factory.post_generation
    def saturation(obj, create, extracted, **kwargs):
        """Attach a conductivity-saturation concept (FR-036)."""
        if not create:
            return
        if extracted is not None:
            obj.saturation.set(extracted)
            return
        attach_random_concept(obj, "saturation", vocabularies.ConductivitySaturation)

    @factory.post_generation
    def pT_conditions(obj, create, extracted, **kwargs):
        """Attach a conductivity pT-conditions concept (FR-036)."""
        if not create:
            return
        if extracted is not None:
            obj.pT_conditions.set(extracted)
            return
        attach_random_concept(
            obj, "pT_conditions", vocabularies.ConductivityPTConditions
        )

    @factory.post_generation
    def pT_function(obj, create, extracted, **kwargs):
        """Attach a conductivity pT-function concept (FR-036)."""
        if not create:
            return
        if extracted is not None:
            obj.pT_function.set(extracted)
            return
        attach_random_concept(obj, "pT_function", vocabularies.ConductivityPTFunction)

    @factory.post_generation
    def strategy(obj, create, extracted, **kwargs):
        """Attach a conductivity-strategy concept (FR-036)."""
        if not create:
            return
        if extracted is not None:
            obj.strategy.set(extracted)
            return
        attach_random_concept(obj, "strategy", vocabularies.ConductivityStrategy)


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

    @factory.post_generation
    def probe_type(obj, create, extracted, **kwargs):
        """Attach a probe-type concept (ConceptManyToManyField; FR-036)."""
        if not create:
            return
        if extracted is not None:
            obj.probe_type.set(extracted)
            return
        attach_random_concept(obj, "probe_type", vocabularies.ProbeType)


class HeatFlowCorrectionFactory(factory.django.DjangoModelFactory):
    """Factory for HeatFlowCorrection (T080).  heat_flow SubFactory is the only
    relation the model requires; correction_type/status are plain choice
    fields, not vocabulary fields.
    """

    heat_flow = factory.SubFactory(HeatFlowFactory)
    correction_type = HeatFlowCorrection.CorrectionTypeChoices.IS
    status = HeatFlowCorrection.StatusChoices.UNSPECIFIED

    class Meta:
        model = HeatFlowCorrection
