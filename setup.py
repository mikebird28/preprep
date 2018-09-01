#!/usr/bin/env python

from distutils.core import setup

requires = [
    "dill",
    "pandas>=0.20.1",
    "xxhash",
    "numpy",
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
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
    ]

)
