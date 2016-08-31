from .conf import CeleryHaystack # this populates our settings
from django.apps import AppConfig


class CeleryHaystackAppConfig(AppConfig):
    name = "celery_haystack"
