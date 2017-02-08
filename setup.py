#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup


with open("README") as f:
    readme = f.read()

with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
    required = f.read().splitlines()

with open(os.path.join(os.path.dirname(__file__), 'test_requirements.txt')) as f:
    test_required = f.read().splitlines() + required

setup(
    name='asyncio_hn',
    version='0.1.5',
    description=" Simple asyncio wrapper to download hackernews",
    long_description=readme + '\n',
    author="Itiel Shwartz",
    author_email='itiel@etlsh.com',
    url='https://github.com/itielshwartz/asyncio_hn',
    packages=[
        'asyncio_hn',
    ],
    include_package_data=True,
    install_requires=required,
    license="MIT license",
    zip_safe=False,
    keywords=['asyncio', 'aiohttp', 'hackernews'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_required,

)
