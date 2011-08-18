#!/usr/bin/env python

"""
Copyright (c) 2011, Scott Burns
All rights reserved.
"""

import os
import sys

import redcap as rc
reload(rc)

study = 'Testing'

import yaml
pycap_file = os.path.expanduser('~/.pycap.yml')
try:
    with open(pycap_file, 'r') as f:
        rc_data = yaml.load(f)
except ImportError:
    rc_data = {}
    
API_Key = rc_data['KEYS'][study]
