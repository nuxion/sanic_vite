# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['changeme',
 'changeme.commands',
 'changeme.html_render',
 'changeme.pages',
 'changeme.services',
 'changeme.types']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.1.1,<4.0.0',
 'click>=8.1.2,<9.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'rich>=12.1.0,<13.0.0',
 'sanic[ext]>=22.3.0,<23.0.0']

entry_points = \
{'console_scripts': ['sbuilder = changeme.cli:cli']}

setup_kwargs = {
    'name': 'changeme',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'nuxion',
    'author_email': 'nuxion@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
