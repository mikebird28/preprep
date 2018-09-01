#!/usr/bin/env python

from distutils.core import setup

requires = [
    "dill",
    "pandas>=0.20.1",
    "xxhash",
    "numpy",
    "pyarrow",
]

setup(name='preprep',
    version='0.01',
    description='Library to make preprocessing more comfortable and quickly',
    author='Keisuke Miura',
    author_email='hello.mikeneko@gmail.com',
    url = 'https://mikebird28.hatenablog.jp/',
    licence = 'MIT',
    packages = ["preprep"],
    install_requires=requires,
)
