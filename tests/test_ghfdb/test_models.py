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
