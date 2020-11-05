#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Scott Burns <scott.s.burns@gmail.com>"
__license__ = "MIT"
__copyright__ = "2014, Vanderbilt University"

import codecs
import os
import re
import sys
import warnings

if sys.version_info[0] < 3:
    warnings.warn(
        "Support Python 2 has been deprecated, and will be removed "
        " in a future major release. Please upgrade to Python 3."
    )

# Taken from vulture setup.py: https://github.com/jendrikseipp/vulture/blob/master/setup.py
def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *parts), "r") as f:
        return f.read()

def find_version(*file_parts):
    version_file = read(*file_parts)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

required = [
    'requests>=1.0.0',
    'semantic-version>=2.3.1'
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
        version=find_version("redcap", "__init__.py"),
        download_url='http://sburns.github.com/PyCap',
        long_description=long_desc,
        packages=['redcap'],
        install_requires=required,
        platforms='any',
        classifiers=(
                'Development Status :: 5 - Production/Stable',
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
