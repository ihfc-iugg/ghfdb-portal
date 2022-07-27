from django.apps import AppConfig

class MainConfig(AppConfig):
    name = 'main'
    verbose_name = 'Main'

    def ready(self):
        from . import signals