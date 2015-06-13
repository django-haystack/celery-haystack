__version__ = '0.9'


def version_hook(config):
    config['metadata']['version'] = __version__
