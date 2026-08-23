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
