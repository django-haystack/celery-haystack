__version__ = '0.7.1'


def version_hook(config):
    config['metadata']['version'] = __version__
