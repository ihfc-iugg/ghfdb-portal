"""Expose the Celery app lazily to avoid a settings import cycle."""


# fairdm -> django_tables2 -> settings would circular-import if celery_app
# were imported eagerly here.
def __getattr__(name):
    """Resolve ``celery_app`` on first access instead of at import time."""
    if name == "celery_app":
        from fairdm.conf.celery import app as celery_app

        globals()["celery_app"] = celery_app
        return celery_app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ("celery_app",)
