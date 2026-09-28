"""App configuration for the review app."""

from django.apps import AppConfig


class GHFDBReviewConfig(AppConfig):
    """Config for the review app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "review"

    def ready(self):
        """Import the app's navigation entries so they register at startup."""
        # Nothing autodiscovers a "menus" module the way Django's own admin
        # autodiscovery finds admin.py, so the import has to happen explicitly.
        from . import menus  # noqa: F401
