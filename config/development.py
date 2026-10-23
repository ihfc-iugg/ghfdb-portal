"""Settings that apply only when ``DJANGO_ENV=development``.

The framework resolves this module by name beside ``config/settings.py`` and
applies it after its own layers, so nothing here can reach a deployed site. The
deployed image sets ``DJANGO_ENV=production`` (the FairDM base image), and the
relaxations below exist purely so a development server is usable from another
device on the local network.
"""

import os

# A development server is reached by hostname from other devices, not only on
# localhost, and DEBUG=True auto-allows localhost alone — so without this any
# other hostname is answered with 400 DisallowedHost.
ALLOWED_HOSTS = ["*"]

# A development server speaks plain HTTP, so a browser discards any cookie
# marked Secure. The failure is silent in one direction only: pages render
# perfectly and every form post comes back 403.
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Without REDIS_URL the baseline CACHES points at a placeholder host that
# django-redis fails to reach silently, which allauth's login rate limiter
# then reads as a permanent block on every login attempt (#216).
if not os.environ.get("REDIS_URL"):
    CACHES = {
        alias: {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": f"dev-{alias}",
        }
        for alias in globals().get("CACHES", {"default": {}})
    }
    # The remote vocabularies are downloaded when the models are imported and kept in a
    # cache, which in process memory goes with the process: every restart of the
    # development server and every test worker downloaded all of them again. On disk they
    # are downloaded once. Delete .vocabularies-cache to download them again. This module
    # runs inside the framework's settings, so ``__file__`` is not this file's path, and
    # the repository root is read from the BASE_DIR they set.
    CACHES["vocabularies"] = {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": globals()["BASE_DIR"] / ".vocabularies-cache",
    }
    VOCABULARY_DEFAULT_CACHE = "vocabularies"
