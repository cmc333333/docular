from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules

from docular.layer.registry import registry


class DocularLayerConfig(AppConfig):
    name = 'docular.layer'

    def ready(self):
        autodiscover_modules('layers', register_to=registry)
