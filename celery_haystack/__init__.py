__version__ = '0.10'


def version_hook(config):
    config['metadata']['version'] = __version__
