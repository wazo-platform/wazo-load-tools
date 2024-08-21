#!/usr/bin/env python3
# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import find_packages, setup

setup(
    name='prometheus_conf_generator',
    version='1.0',
    author='Wazo Authors',
    description='Prometheus configuration generator',
    author_email='dev@wazo.io',
    url='https://wazo-platform.org',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'prom-conf-generator=prom_conf_generator.main:main',
        ],
    },
)
