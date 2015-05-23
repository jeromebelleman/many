#!/usr/bin/env python
# coding=utf-8

import os
from distutils.core import setup

delattr(os, 'link')

setup(
    name='many',
    version='1.0',
    author='Jerome Belleman',
    author_email='Jerome.Belleman@gmail.com',
    url='http://cern.ch/jbl',
    description="Perform changes on many images",
    long_description="GUI to perform changes on many images.",
    scripts=['Many.py'],
    data_files=[('share/man/man1', ['many.1'])],
)
