__version__ = '0.10'


# this is not a django AppConfig object and therefore needs to be imported here so other tasks can subclass CeleryHaystackSignalHandler
from .conf import CeleryHaystack


def version_hook(config):
    config['metadata']['version'] = __version__
