from .conf import CeleryHaystack # this populates our settings
from django.apps import apps as django_apps


class CeleryHaystackAppConfig(django_apps.AppConfig):
    name = "celery_haystack"
