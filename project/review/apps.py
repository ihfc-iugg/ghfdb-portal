from django.apps import AppConfig


class GHFDBReviewConfig(AppConfig):
    """Config for heat flow schema"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "review"
