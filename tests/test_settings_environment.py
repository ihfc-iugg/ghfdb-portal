"""The settings module is loaded in every environment, production included.

`deploy/Dockerfile` sets ``DJANGO_SETTINGS_MODULE=config.settings`` alongside
``DJANGO_ENV=production``, so a relaxation written unguarded into
``config/settings.py`` is a relaxation on the public site. These tests read the
module's source rather than the resolved settings, because the resolved value
depends on the environment the suite itself runs in.
"""

import ast
from pathlib import Path

import pytest

SETTINGS = Path(__file__).resolve().parents[1] / "config" / "settings.py"

RELAXATIONS = ("ALLOWED_HOSTS", "SESSION_COOKIE_SECURE", "CSRF_COOKIE_SECURE")


def _module():
    return ast.parse(SETTINGS.read_text())


def _top_level_assignments(tree):
    """Names assigned at module level, outside any conditional."""
    names = set()
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


@pytest.mark.parametrize("name", RELAXATIONS)
def test_relaxation_is_not_assigned_unconditionally(name):
    assert name not in _top_level_assignments(_module()), (
        f"{name} is assigned at module level in config/settings.py, which the "
        "production image loads. Guard it on DJANGO_ENV."
    )


def test_the_development_guard_reads_django_env():
    """The guard exists and keys on the variable the Dockerfile sets."""
    source = SETTINGS.read_text()
    assert 'os.environ.get("DJANGO_ENV"' in source
    assert '== "development"' in source


def test_the_dockerfile_still_loads_this_module():
    """If this stops being true the guard above is protecting nothing, and the
    reasoning behind it needs revisiting rather than the test deleting."""
    dockerfile = (
        Path(__file__).resolve().parents[1] / "deploy" / "Dockerfile"
    ).read_text()
    assert "DJANGO_SETTINGS_MODULE=config.settings" in dockerfile
    assert "DJANGO_ENV=production" in dockerfile
