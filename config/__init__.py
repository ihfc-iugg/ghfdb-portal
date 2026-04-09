# Defer Celery import to avoid circular import when Django loads settings.
# The celery app is imported lazily to prevent fairdm → django_tables2 → settings
# circular dependency during manage.py commands.
def __getattr__(name):
    if name == "celery_app":
        from fairdm.conf.celery import app as celery_app

        globals()["celery_app"] = celery_app
        return celery_app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ("celery_app",)
