from django.apps import AppConfig


class GHFDBReviewConfig(AppConfig):
    """Config for heat flow schema"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "review"

    def ready(self):
        # Registers this app's navigation entry into mvp's AppMenu
        # (T013). Nothing autodiscovers a "menus" module the way Django's
        # own admin autodiscovery finds admin.py, so the import has to
        # happen explicitly, once, at startup.
        from . import menus  # noqa: F401
