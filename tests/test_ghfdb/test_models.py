"""
Smoke tests for the GHFDB proxy model.
"""


def test_ghfdb_proxy_meta():
    """T018: GHFDB must be a proxy model with the correct verbose_name."""
    from project.ghfdb.models import GHFDB

    assert GHFDB._meta.proxy is True
    assert str(GHFDB._meta.verbose_name) == "GHFDB Entry"
    assert str(GHFDB._meta.verbose_name_plural) == "GHFDB Entries"


def test_ghfdb_parent_proxy_meta():
    """T074 (US1b): GHFDBParent must be a proxy model with the correct verbose_name."""
    from project.ghfdb.models import GHFDBParent

    assert GHFDBParent._meta.proxy is True
    assert str(GHFDBParent._meta.verbose_name) == "GHFDB Parent Entry"
    assert str(GHFDBParent._meta.verbose_name_plural) == "GHFDB Parent Entries"
