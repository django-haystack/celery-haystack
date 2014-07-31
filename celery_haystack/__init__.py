__version__ = '0.8'


def version_hook(config):
    config['metadata']['version'] = __version__
