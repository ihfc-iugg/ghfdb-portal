"""Relaxations belong to an environment module, never to the shared one.

`deploy/Dockerfile` sets ``DJANGO_SETTINGS_MODULE=config.settings`` alongside
``DJANGO_ENV=production``, so ``config/settings.py`` is loaded on the public
site as well as in development. The framework resolves ``config/<env>.py``
beside it and applies only the one matching ``DJANGO_ENV``, which is where
anything relaxed for a development server has to live.

These tests read the modules' source rather than the resolved settings, because
the resolved value depends on the environment the suite itself runs in.
"""

import ast
from pathlib import Path

import pytest

CONFIG = Path(__file__).resolve().parents[1] / "config"
SHARED = CONFIG / "settings.py"
DEVELOPMENT = CONFIG / "development.py"

RELAXATIONS = ("ALLOWED_HOSTS", "SESSION_COOKIE_SECURE", "CSRF_COOKIE_SECURE")


def _assigned_names(path):
    """Every name the module assigns, at any nesting depth."""
    names = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


@pytest.mark.parametrize("name", RELAXATIONS)
def test_the_shared_settings_module_relaxes_nothing(name):
    assert name not in _assigned_names(SHARED), (
        f"{name} is assigned in config/settings.py, which the production image "
        "loads. Environment-specific settings belong in config/development.py."
    )


@pytest.mark.parametrize("name", RELAXATIONS)
def test_the_development_module_carries_the_relaxation(name):
    assert name in _assigned_names(DEVELOPMENT)


def test_the_dockerfile_still_loads_the_shared_module_in_production():
    """If this stops being true, the separation above is protecting nothing and
    the reasoning needs revisiting rather than the test deleting."""
    dockerfile = (
        Path(__file__).resolve().parents[1] / "deploy" / "Dockerfile"
    ).read_text()
    assert "DJANGO_SETTINGS_MODULE=config.settings" in dockerfile
    assert "DJANGO_ENV=production" in dockerfile


def test_no_production_module_relaxes_them_either():
    """``config/production.py`` is resolved by the same mechanism under
    ``DJANGO_ENV=production``, so it is subject to the same rule."""
    production = CONFIG / "production.py"
    if not production.exists():
        pytest.skip("this project has no production override module")
    for name in RELAXATIONS:
        assert name not in _assigned_names(production)
