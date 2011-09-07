#!/usr/bin/env python

"""
Copyright (c) 2011, Scott Burns
All rights reserved.
"""

import os
import sys
import json

import redcap
reload(redcap)
reload(redcap.rc)

study = 'Testing'

import yaml
pycap_file = os.path.expanduser('~/.pycap.yml')
try:
    with open(pycap_file, 'r') as f:
        rc_data = yaml.load(f)
except ImportError:
    rc_data = {}
    
API_Key = rc_data['KEYS'][study]

url = 'https://redcap.vanderbilt.edu/api/'

project = redcap.Project(url, API_Key)


pl = {'token':API_Key, 'content':'record', 'type':'eav', 'overwriteBehavior':'normal'}

pl['format'] = 'json'
data = {'study_id':'1',
        'first_name':'John',
        'last_name':'Doe',
        'dob':'2000-01-01',
        'sex':'M',
        'foo_score':'1',
        'bar_score':'2',
        'image_path':'/path/to/image'}

jData = json.dumps(data,separators=(',',':'))
pl['data'] = jData

a = redcap.rc.RCRequest(url, pl, 'imp_record').execute()

