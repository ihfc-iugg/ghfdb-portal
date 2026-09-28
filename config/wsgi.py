"""Expose the WSGI application under ``WSGI_APPLICATION``."""

import os
import sys

from django.core.wsgi import get_wsgi_application

# so that apps can be imported from the project directory
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "project"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
