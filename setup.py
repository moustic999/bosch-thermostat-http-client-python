#!/usr/bin/env python
# -*- coding:utf-8 -*-
from setuptools import setup

VERSION = '0.1.0'

REQUIRES = [
    'pyaes>=1.6.1',
    'aiohttp>=3.5.4'
    ]


setup(
    name='bosh-thermostat-http-client',
    version=VERSION,
    description='Python API and command line tool for talking to Bosch™ Thermostat using HTTP ',
     author='Ludovic Laurent',
    author_email='ludovic.laurent@gmail.com',
    maintainer='Ludovic Laurent',
    maintainer_email='ludovic.laurent@gmail.com',
    url='https://github.com/moustic999/bosch-thermostat-http-client-python.git',
    download_url='https://github.com/patvdleer/bosch-thermostat-http-client-python/archive/{}.zip'.format(VERSION),
    packages=["bosch_thermostat_http"],
    install_requires=REQUIRES,
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