
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Simple python pagin class',
    'author': 'Andy Stanberry',
    'url': 'https://github.com/yarnbasket/pyager',
    'download_url': 'https://github.com/yarnbasket/pyager/releases',
    'author_email': 'andy@yarn.is',
    'version': '0.2',
    'install_requires': [],
    'packages': ['pyager'],
    'scripts': [],
    'name': 'pyager'
}

setup(**config)
