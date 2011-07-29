from os import path
import codecs
from setuptools import setup

setup(
    name='celery-haystack',
    version=":versiontools:celery_haystack:",
    description='An app for integrating Celery with Haystack.',
    long_description=codecs.open(path.join(path.dirname(__file__), 'README.rst')).read(),
    author='Jannis Leidel',
    author_email='jannis@leidel.info',
    url='http://github.com/jezdez/celery-haystack',
    packages=['celery_haystack'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    setup_requires=[
        'versiontools >= 1.5',
    ],
)
