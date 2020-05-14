from django.apps import AppConfig


class ReferenceConfig(AppConfig):
    name = 'reference'

    def ready(self):
        import reference.signals  # noqa