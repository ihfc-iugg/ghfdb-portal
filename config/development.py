"""Settings that apply only when ``DJANGO_ENV=development``.

The framework resolves this module by name beside ``config/settings.py`` and
applies it after its own layers, so nothing here can reach a deployed site. The
deployed image sets ``DJANGO_ENV=production`` (``deploy/Dockerfile``), and the
relaxations below exist purely so a development server is usable from another
device on the local network.
"""

# A development server is reached by hostname from other devices, not only on
# localhost, and DEBUG=True auto-allows localhost alone — so without this any
# other hostname is answered with 400 DisallowedHost.
ALLOWED_HOSTS = ["*"]

# A development server speaks plain HTTP, so a browser discards any cookie
# marked Secure. The failure is silent in one direction only: pages render
# perfectly and every form post comes back 403.
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
