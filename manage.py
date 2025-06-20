#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # so that apps in the project directory are discovered
    sys.path.append(os.path.join(os.path.dirname(__file__), "project"))
    os.environ.setdefault("DJANGO_ENV", "development")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        try:
            import django  # noqa: F401
        except ImportError as err:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            ) from err

        raise

    execute_from_command_line(sys.argv)
