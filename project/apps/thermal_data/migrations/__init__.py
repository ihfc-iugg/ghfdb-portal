"""Configuration of your project is located within the `project`
folder at the root level of your application. This folder is
what Django would create if you `start a new project`_ using the command
`django-admin startproject project`. It includes one additional
module called ``dashboard.py`` which configures the dashboard
in the admin site.

.. _start a new project: link: https://docs.djangoproject.com/en/4.1/intro/tutorial01/#creating-a-project
"""
# import drf_auto_endpoint.factories
from geoluminate.backends.celery import app as celery_app

__all__ = ("celery_app",)
