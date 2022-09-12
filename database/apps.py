from django.apps import AppConfig
from django.core.signals import request_finished

class DatabaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'database'
    verbose_name = 'Global Heat Flow Database'

    def ready(self):
        from . import signals