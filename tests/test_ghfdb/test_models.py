"""
Smoke tests for the GHFDB proxy model.
"""


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
