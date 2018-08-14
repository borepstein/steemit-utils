from __future__ import absolute_import

import os
from setuptools import setup, find_packages

install_requires = [
    "steem"
    ]

package_data = {}

s = setup(
    name='steemitutils',
    version='0.1',
        package_data = package_data,
    install_requires = install_requires,
    author = "Boris Epstein",
    author_email = "borepstein@gmail.com",
    description = 'API Wrapper around STEEM blockchain',
    long_description = open('README.md').read(),
    license = "GNU",
    keywords = "steemit blockchain",
    url = "https://github.com/borepstein/steem-python",
    packages = find_packages(exclude=['tests'])
)
