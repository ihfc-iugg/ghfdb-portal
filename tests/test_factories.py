"""Tests for tests/factories.py.

Every test needing an assessment, a claimed person, a ghost person or a
publication gets one from a factory here — reusing the framework's own
factories (``DatasetFactory``, ``LiteratureItemFactory``, ``PersonFactory``)
rather than redefining them.

T076–T081 — US6: every model has test data, including its vocabulary fields
(FR-035–FR-037).
"""

import pytest
from fairdm.factories import LiteratureItemFactory, PersonFactory
from heat_flow.models import (
    HeatFlow,
    HeatFlowSite,
    IntervalConductivity,
    ProbeMetadata,
    ThermalGradient,
)
from research_vocabs.models import Concept

from tests.factories import ReviewFactory


@pytest.mark.django_db
@pytest.mark.review
class TestReviewFactories:
    def test_review_factory_produces_a_saved_instance(self):
        review = ReviewFactory()

        assert review.pk is not None
        assert review.literature_id is not None
        assert review.dataset_id is not None

    def test_person_factory_with_is_claimed_true_produces_a_claimed_person(self):
        person = PersonFactory(is_claimed=True, password="test-pass-123")

        assert person.pk is not None
        assert person.is_claimed is True
        assert person.has_usable_password()

    def test_person_factory_with_email_none_produces_an_unclaimed_person_with_no_email(
        self,
    ):
        person = PersonFactory(email=None, is_claimed=False)

        assert person.pk is not None
        assert person.is_claimed is False
        assert person.email is None

    def test_literature_item_factory_is_reused_from_the_framework(self):
        """A publication is supplied by the framework's own factory, not a
        review-specific redefinition of it."""
        item = LiteratureItemFactory()

        assert item.pk is not None


def concepts_of(model, field_name):
    """Concept primary keys of the vocabulary *the field itself declares*.

    Deriving it from ``<field>_vocab`` rather than naming a vocabulary class in the
    test is deliberate: a test that names the vocabulary independently passes when the
    field and the factory are re-pointed at a different one together, which is exactly
    the drift these assertions exist to catch.
    """
    vocabulary = getattr(model, f"{field_name}_vocab")
    # `<field>_vocab` is the instantiated vocabulary; get_for_vocabulary expects the
    # class, which it instantiates itself (research_vocabs/models.py:167).
    return set(
        Concept.get_for_vocabulary(type(vocabulary)).values_list("pk", flat=True)
    )


class TestHeatFlowFactories:
    """T076 — every factory called with no arguments returns a saved instance."""

    @pytest.mark.django_db
    def test_all_factories_produce_saved_instances(self):
        """
        T076 – Each of the 8 factory classes creates a saved instance with a
        non-null PK in a single call (FR-035).
        """
        from tests.factories import (
            HeatFlowCorrectionFactory,
            HeatFlowFactory,
            HeatFlowIntervalFactory,
            HeatFlowSiteFactory,
            IntervalConductivityFactory,
            ParentHeatFlowFactory,
            ProbeMetadataFactory,
            ThermalGradientFactory,
        )

        assert HeatFlowSiteFactory().pk is not None
        assert HeatFlowIntervalFactory().pk is not None
        assert ParentHeatFlowFactory().pk is not None
        assert ThermalGradientFactory().pk is not None
        assert IntervalConductivityFactory().pk is not None
        assert HeatFlowFactory().pk is not None
        assert ProbeMetadataFactory().pk is not None
        assert HeatFlowCorrectionFactory().pk is not None

    @pytest.mark.django_db
    def test_heat_flow_site_factory_save(self):
        """T076 – HeatFlowSiteFactory smoke test."""
        from tests.factories import HeatFlowSiteFactory

        assert HeatFlowSiteFactory().pk is not None

    @pytest.mark.django_db
    def test_heat_flow_interval_factory_save(self):
        """T076 – HeatFlowIntervalFactory smoke test; site FK populated via SubFactory."""
        from tests.factories import HeatFlowIntervalFactory

        interval = HeatFlowIntervalFactory()
        assert interval.pk is not None
        assert interval.site_id is not None

    @pytest.mark.django_db
    def test_parent_heat_flow_factory_save(self):
        """T076 – ParentHeatFlowFactory smoke test; creates a ParentHeatFlow with a HeatFlowSite sample."""
        from tests.factories import ParentHeatFlowFactory

        parent = ParentHeatFlowFactory()
        assert parent.pk is not None
        assert (
            parent.sample_id is not None
        )  # SubFactory(HeatFlowSiteFactory) provides a valid site

    @pytest.mark.django_db
    def test_probe_metadata_factory_save(self):
        """T076 – ProbeMetadataFactory smoke test; interval SubFactory creates linked interval."""
        from tests.factories import ProbeMetadataFactory

        probe = ProbeMetadataFactory()
        assert probe.pk is not None
        assert probe.interval_id is not None

    @pytest.mark.django_db
    def test_heat_flow_correction_factory_save(self):
        """T076/T080 – HeatFlowCorrectionFactory smoke test; heat_flow SubFactory creates the parent record."""
        from tests.factories import HeatFlowCorrectionFactory

        correction = HeatFlowCorrectionFactory()
        assert correction.pk is not None
        assert correction.heat_flow_id is not None


class TestFactoriesCreateRequiredRelations:
    """T077 — every factory creates whatever related records its model requires."""

    @pytest.mark.django_db
    def test_heat_flow_factory_creates_its_interval_sample(self):
        from heat_flow.models import HeatFlowInterval

        from tests.factories import HeatFlowFactory

        child = HeatFlowFactory()
        assert isinstance(child.sample, HeatFlowInterval)

    @pytest.mark.django_db
    def test_thermal_gradient_factory_creates_its_interval_sample(self):
        from heat_flow.models import HeatFlowInterval

        from tests.factories import ThermalGradientFactory

        gradient = ThermalGradientFactory()
        assert isinstance(gradient.sample, HeatFlowInterval)

    @pytest.mark.django_db
    def test_interval_conductivity_factory_creates_its_interval_sample(self):
        from heat_flow.models import HeatFlowInterval

        from tests.factories import IntervalConductivityFactory

        conductivity = IntervalConductivityFactory()
        assert isinstance(conductivity.sample, HeatFlowInterval)

    @pytest.mark.django_db
    def test_parent_heat_flow_factory_creates_its_site_sample(self):
        from heat_flow.models import HeatFlowSite

        from tests.factories import ParentHeatFlowFactory

        parent = ParentHeatFlowFactory()
        assert isinstance(parent.sample, HeatFlowSite)

    @pytest.mark.django_db
    def test_probe_metadata_factory_creates_its_interval(self):
        from heat_flow.models import HeatFlowInterval

        from tests.factories import ProbeMetadataFactory

        probe = ProbeMetadataFactory()
        assert isinstance(probe.interval, HeatFlowInterval)

    @pytest.mark.django_db
    def test_heat_flow_correction_factory_creates_its_heat_flow(self):
        from heat_flow.models import HeatFlow

        from tests.factories import HeatFlowCorrectionFactory

        correction = HeatFlowCorrectionFactory()
        assert isinstance(correction.heat_flow, HeatFlow)


class TestFactoryVocabularyPopulation:
    """T078/T081 — factories populate controlled-vocabulary fields with concepts
    drawn from each field's own vocabulary.

    Membership is asserted against ``Concept.get_for_vocabulary()`` — the same
    lookup the factories use — never merely that the field is non-empty.
    """

    @pytest.mark.django_db
    def test_heat_flow_site_scalar_concept_fields_are_members_of_their_vocabularies(
        self,
    ):
        from tests.factories import HeatFlowSiteFactory

        site = HeatFlowSiteFactory()

        assert str(site.environment) in HeatFlowSite.environment_vocab.values
        assert str(site.explo_method) in HeatFlowSite.explo_method_vocab.values

    @pytest.mark.django_db
    def test_heat_flow_site_explo_purpose_concepts_belong_to_exploration_purpose_vocabulary(
        self,
    ):
        from tests.factories import HeatFlowSiteFactory

        site = HeatFlowSiteFactory()

        expected = concepts_of(HeatFlowSite, "explo_purpose")
        attached = set(site.explo_purpose.values_list("pk", flat=True))

        assert attached
        assert attached <= expected

    @pytest.mark.django_db
    def test_heat_flow_method_concepts_belong_to_heat_flow_method_vocabulary(self):
        from tests.factories import HeatFlowFactory

        child = HeatFlowFactory()

        expected = concepts_of(HeatFlow, "method")
        attached = set(child.method.values_list("pk", flat=True))

        assert attached
        assert attached <= expected

    @pytest.mark.django_db
    def test_thermal_gradient_method_and_correction_concepts_belong_to_their_vocabularies(
        self,
    ):
        from tests.factories import ThermalGradientFactory

        gradient = ThermalGradientFactory()

        expected_method = concepts_of(ThermalGradient, "method_top")
        expected_correction = concepts_of(ThermalGradient, "correction_top")

        for field_name, expected in (
            ("method_top", expected_method),
            ("method_bottom", expected_method),
            ("correction_top", expected_correction),
            ("correction_bottom", expected_correction),
        ):
            attached = set(getattr(gradient, field_name).values_list("pk", flat=True))
            assert attached, field_name
            assert attached <= expected, field_name

    @pytest.mark.django_db
    def test_interval_conductivity_concepts_belong_to_their_vocabularies(self):
        from tests.factories import IntervalConductivityFactory

        conductivity = IntervalConductivityFactory()

        for field_name in (
            "source",
            "location",
            "method",
            "saturation",
            "pT_conditions",
            "pT_function",
            "strategy",
        ):
            expected = concepts_of(IntervalConductivity, field_name)
            attached = set(
                getattr(conductivity, field_name).values_list("pk", flat=True)
            )
            assert attached, field_name
            assert attached <= expected, field_name

    @pytest.mark.django_db
    def test_probe_metadata_probe_type_concepts_belong_to_probe_type_vocabulary(self):
        from tests.factories import ProbeMetadataFactory

        probe = ProbeMetadataFactory()

        expected = concepts_of(ProbeMetadata, "probe_type")
        attached = set(probe.probe_type.values_list("pk", flat=True))

        assert attached
        assert attached <= expected


class TestCompleteFactoryGraph:
    """T079 — the complete graph is buildable from factory calls alone, and the
    relationships resolve.
    """

    @pytest.mark.django_db
    def test_site_through_parent_graph_resolves_via_factories_alone(self):
        from tests.factories import (
            HeatFlowFactory,
            HeatFlowIntervalFactory,
            HeatFlowSiteFactory,
            IntervalConductivityFactory,
            ParentHeatFlowFactory,
            ThermalGradientFactory,
        )

        site = HeatFlowSiteFactory()
        interval = HeatFlowIntervalFactory(site=site)
        gradient = ThermalGradientFactory(sample=interval)
        conductivity = IntervalConductivityFactory(sample=interval)
        parent = ParentHeatFlowFactory(sample=site)
        child = HeatFlowFactory(
            sample=interval,
            parent=parent,
            thermal_gradient=gradient,
            thermal_conductivity=conductivity,
        )

        assert interval.site == site
        assert gradient.sample == interval
        assert conductivity.sample == interval
        assert parent.sample == site
        assert child.sample == interval
        assert child.parent == parent
        assert child.thermal_gradient == gradient
        assert child.thermal_conductivity == conductivity
        assert child in parent.children.all()
        assert child in gradient.heat_flow_children.all()
        assert child in conductivity.heat_flow_children.all()
