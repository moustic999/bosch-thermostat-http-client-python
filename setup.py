#!/usr/bin/env python
# -*- coding:utf-8 -*-
from setuptools import setup

VERSION = '0.4.3'

REQUIRES = [
    'pyaes>=1.6.1',
    'aiohttp'
    ]

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='bosch-thermostat-http-client',
    version=VERSION,
    description='Python API for talking to Bosch™ Heating gateway using HTTP ',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Ludovic Laurent',
    author_email='ludovic.laurent@gmail.com',
    maintainer='Ludovic Laurent',
    maintainer_email='ludovic.laurent@gmail.com',
    url='https://github.com/moustic999/bosch-thermostat-http-client-python.git',
    download_url='https://github.com/moustic999/bosch-thermostat-http-client-python/archive/{}.zip'.format(VERSION),
    packages=["bosch_thermostat_http"],
    install_requires=REQUIRES,
    include_package_data = True,
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Environment :: Console',
        'Topic :: Other/Nonlisted Topic',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
)