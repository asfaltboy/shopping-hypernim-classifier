# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme = ''

setup(
    long_description=readme,
    name='hyper_shopping',
    version='0.0.0',
    packages=['hyper_shopping'],
    package_data={
        'hyper_shopping': ['.pytest_cache/*.TAG', '.pytest_cache/*.md']
    },
    install_requires=[
        'click', 'click-repl', 'ipython', 'mypy', 'mypy-extensions', 'nltk',
        'pyspellchecker', 'pytest', 'pytest-mypy'
    ],
)
