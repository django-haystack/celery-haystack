import re
from os import path
import codecs
from setuptools import setup, find_packages


def read(*parts):
    return codecs.open(path.join(path.dirname(__file__), *parts)).read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name='celery-haystack',
    version=find_version("celery_haystack", "__init__.py"),
    description='An app for integrating Celery with Haystack.',
    long_description=read('README.rst'),
    author='Jannis Leidel',
    author_email='jannis@leidel.info',
    url='http://celery-haystack.rtfd.org/',
    packages=find_packages(),
    license='BSD',
    classifiers=[
        "Development Status :: 4 - Beta",
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
    install_requires=[
        'django-appconf >= 0.4.1',
    ],
    zip_safe=False,
)
