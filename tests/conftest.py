"""
Configuration for pytest.

This file configures the test environment for Django.
"""

import os

import django


def pytest_configure():
    """Configure Django for testing."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    os.environ.setdefault("DJANGO_ENV", "development")
    django.setup()
