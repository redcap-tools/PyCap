#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2011, Scott Burns
All rights reserved.
"""

import os
import sys
import redcap

from distutils.core import setup
    

DISTNAME = 'PyCap'
DESCR = """PyCap: Python interface to REDCap"""
MAINTAINER = 'Scott Burns'
MAINTAINER_EMAIL = 'scott.s.burns@gmail.com'
URL = 'http://github.com/VUIIS/PyCap'
LICENSE = 'BSD (3-clause)'
DOWNLOAD_URL = 'https://github.com/VUIIS/PyCap'
VERSION = redcap.__version__

if __name__ == '__main__':

    set(name=DISTNAME,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        description=DESCR,
        license=LICENSE,
        url=URL,
        version=VERSION,
        download_url=DOWNLOAD_URL,
        long_description=open('README.md').read() + '\n\n'
        packages=['redcap', 'tests'],
        install_requires=[],
        classifiers=(
                'Development Status :: 4 - Beta',
                'Intended Audience :: Developers',
                'Intended Audience :: Science/Research',
                'License :: OSI Approved',
                'Topic :: Software Development',
                'Topic :: Scientific/Engineering',
                'Operating System :: Microsoft :: Windows',
                'Operating System :: POSIX',
                'Operating System :: Unix',
                'Operating System :: MacOS'
                'Programming Language :: Python',
                'Programming Language :: Python :: 2.5',
                'Programming Language :: Python :: 2.6',
                'Programming Language :: Python :: 2.7',)
        )
        
