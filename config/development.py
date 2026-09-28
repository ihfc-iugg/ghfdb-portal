"""Settings that apply only when ``DJANGO_ENV=development``.

The framework resolves this module by name beside ``config/settings.py`` and
applies it after its own layers, so nothing here can reach a deployed site. The
deployed image sets ``DJANGO_ENV=production`` (``deploy/Dockerfile``), and the
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
