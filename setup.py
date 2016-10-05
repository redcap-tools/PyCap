#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Scott Burns <scott.s.burns@gmail.com>'
__license__ = 'MIT'
__copyright__ = '2014, Vanderbilt University'

import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version():
    base = os.path.dirname(__file__)
    with open(os.path.join(base, 'redcap/version.py')) as f:
        VERSION = None
        exec(f.read())
        return VERSION

required = [
    'requests>=1.0.0',
    'semantic-version==2.3.1'
]

if __name__ == '__main__':
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')

    long_desc = open('README.rst').read() + '\n\n' + open('HISTORY.rst').read()

    setup(name='PyCap',
        maintainer='Scott Burns',
        maintainer_email='scott.s.burns@gmail.com',
        description="""PyCap: Python interface to REDCap""",
        license='MIT',
        url='http://sburns.github.com/PyCap',
        version=get_version(),
        download_url='http://sburns.github.com/PyCap',
        long_description=long_desc,
        packages=['redcap'],
        install_requires=required,
        platforms='any',
        classifiers=(
                'Development Status :: 5 - Production',
                'Intended Audience :: Developers',
                'Intended Audience :: Science/Research',
                'License :: OSI Approved :: MIT License',
                'License :: OSI Approved',
                'Topic :: Software Development',
                'Topic :: Scientific/Engineering',
                'Operating System :: Microsoft :: Windows',
                'Operating System :: POSIX',
                'Operating System :: Unix',
                'Operating System :: MacOS',
                'Programming Language :: Python',
                'Programming Language :: Python :: 2.7',)
        )
