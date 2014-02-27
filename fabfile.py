#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Scott Burns <scott.s.burns@vanderbilt.edu>'
__license__ = 'MIT'
__copyright__ = '2014, Vanderbilt University'

from fabric.api import local, lcd


def upload():
    local('python setup.py register')
    local('python setup.py sdist upload')
    local('python setup.py bdist_wheel upload')


def rebuild():
    clean()
    local("python setup.py develop -u")
    local("python setup.py clean")
    local("python setup.py install")
    clean()


def clean():
    local("""find redcap -type f -name "*.pyc" -exec rm {} \;""")
    local("rm -rf build")
    local("rm -rf dist")
    local("rm -rf Rosie.egg-info")


def test():
    local('nosetests -v -w test/')

def doc():
    with lcd('docs'):
        local('make html')
