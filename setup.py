from setuptools import setup, find_packages

setup(
    name='celery-haystack',
    version=":versiontools:celery_haystack:",
    description='An app for integrating Celery with Haystack.',
    author='Jannis Leidel',
    author_email='jannis@leidel.info',
    url='http://github.com/jezdez/celery-haystack',
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
    setup_requires = [
        'versiontools >= 1.5',
    ],
)
