#! /usr/bin/env python3
"""
proxyget -- setup.py

author  - fmitchell
created - 2019-Jan-25
"""

from setuptools import setup, find_packages

setup(
        name='proxyget',
        version='0.3.0',
        description='Tools for downloading past corporate proxies',
        author='FHT Mitchell',
        author_email='f.mitchell@sstl.co.uk',
        python_requires='>=3.6.0',
        install_requires=['requests>=2.19.1'],
        packages=find_packages()
)
