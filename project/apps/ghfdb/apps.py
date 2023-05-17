from django.apps import AppConfig


class GHFDBConfig(AppConfig):
    """Config for the Global Heat Flow Database application"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "ghfdb"
    verbose_name = "Global Heat Flow Database"
