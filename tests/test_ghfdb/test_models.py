"""
Smoke tests for the GHFDB proxy model.
"""

import pytest

pytestmark = pytest.mark.ghfdb


class TestGHFDBProxyModels:
    """GHFDB proxy models must expose the correct Meta configuration."""

    def test_ghfdb_proxy_meta(self):
        """T018: GHFDBChild must be a proxy model with the correct verbose_name."""
        from project.ghfdb.models import GHFDBChild

        assert GHFDBChild._meta.proxy is True
        assert str(GHFDBChild._meta.verbose_name) == "GHFDB Child"
        assert str(GHFDBChild._meta.verbose_name_plural) == "GHFDB Children"

    def test_ghfdb_parent_proxy_meta(self):
        """T074 (US1b): GHFDBParent must be a proxy model with the correct verbose_name."""
        from project.ghfdb.models import GHFDBParent

        assert GHFDBParent._meta.proxy is True
        assert str(GHFDBParent._meta.verbose_name) == "GHFDB Parent"
        assert str(GHFDBParent._meta.verbose_name_plural) == "GHFDB Parents"


class TestFixtures:
    """The Phase 1 fixture contracts every later phase is held to (T002-T010)."""

    def test_vocabulary_concepts_are_present(self, db):
        """T002: the autouse concept preload covers every vocabulary this
        feature filters on."""
        from research_vocabs.models import Concept

        from heat_flow.vocabularies import (
            ExplorationMethod,
            ExplorationPurpose,
            GeographicEnvironment,
        )

        for vocabulary in (GeographicEnvironment, ExplorationMethod, ExplorationPurpose):
            assert Concept.get_for_vocabulary(vocabulary).exists(), (
                f"no concepts preloaded for {vocabulary.__name__}"
            )

    def test_dataset_fixture_is_saved(self, dataset):
        """T003: ``dataset`` wraps ``DatasetFactory`` and is persisted."""
        assert dataset.pk is not None

    def test_published_chain_is_complete(self, published_chain):
        """T004: every relationship the chain names resolves, and both
        published identifiers are set."""
        child = published_chain
        parent = child.parent
        interval = child.sample
        site = interval.site

        assert site is not None
        assert hasattr(interval, "probe_metadata")
        assert child.thermal_gradient is not None
        assert child.thermal_conductivity is not None
        assert child.corrections.count() == 9
        assert parent.ghfdb_id is not None
        assert child.ghfdb_id is not None

    def test_published_chains_builds_the_number_asked_for(self, published_chains):
        """T005: the callable builds exactly as many chains as it is asked
        for, at two different sizes (R2)."""
        from heat_flow.models import HeatFlow

        first_batch = published_chains(2)
        assert len(first_batch) == 2
        assert HeatFlow.objects.count() == 2

        second_batch = published_chains(4)
        assert len(second_batch) == 4
        assert HeatFlow.objects.count() == 6

    def test_unpublished_chain_has_no_published_identifier(self, unpublished_chain):
        """T006: neither level carries a published identifier (SC-005)."""
        assert unpublished_chain.ghfdb_id is None
        assert unpublished_chain.parent.ghfdb_id is None

    def test_partial_chains_omit_only_what_they_name(
        self,
        chain_without_gradient,
        chain_without_conductivity,
        chain_without_probe_metadata,
        chain_missing_correction,
    ):
        """T007: each partial-chain fixture omits exactly the one piece it
        names, and every other relationship still resolves."""
        assert chain_without_gradient.thermal_gradient is None
        assert chain_without_gradient.thermal_conductivity is not None
        assert hasattr(chain_without_gradient.sample, "probe_metadata")
        assert chain_without_gradient.corrections.count() == 9

        assert chain_without_conductivity.thermal_conductivity is None
        assert chain_without_conductivity.thermal_gradient is not None
        assert hasattr(chain_without_conductivity.sample, "probe_metadata")
        assert chain_without_conductivity.corrections.count() == 9

        assert not hasattr(chain_without_probe_metadata.sample, "probe_metadata")
        assert chain_without_probe_metadata.thermal_gradient is not None
        assert chain_without_probe_metadata.thermal_conductivity is not None
        assert chain_without_probe_metadata.corrections.count() == 9

        missing = chain_missing_correction("IS")
        assert not missing.corrections.filter(correction_type="IS").exists()
        assert missing.corrections.count() == 8
        assert missing.thermal_gradient is not None
        assert missing.thermal_conductivity is not None
        assert hasattr(missing.sample, "probe_metadata")

    def test_sites_by_contribution_covers_the_four_shapes(self, sites_by_contribution):
        """T008: the four contribution shapes SC-004 names, and one site
        carrying two exploration purposes so the many-valued parent column
        is exercised."""
        all_contributing = sites_by_contribution["all_contributing"]
        some_contributing = sites_by_contribution["some_contributing"]
        none_contributing = sites_by_contribution["none_contributing"]
        no_determinations = sites_by_contribution["no_determinations"]

        assert all_contributing.children.count() == 2
        assert all_contributing.children.filter(is_relevant=True).count() == 2

        assert some_contributing.children.count() == 2
        assert some_contributing.children.filter(is_relevant=True).count() == 1

        assert none_contributing.children.count() == 2
        assert none_contributing.children.filter(is_relevant=True).count() == 0

        assert no_determinations.children.count() == 0

        purpose_counts = {
            parent.sample.explo_purpose.count()
            for parent in sites_by_contribution.values()
        }
        assert 2 in purpose_counts

    def test_staff_client_reaches_the_admin_index(self, staff_client):
        """T009: the staff client holds enough permission to reach the admin
        index."""
        from django.urls import reverse

        response = staff_client.get(reverse("admin:index"))
        assert response.status_code == 200
