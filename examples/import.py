#!/usr/bin/env python

"""
Copyright (c) 2011, Scott Burns
All rights reserved.
"""

import os
from ConfigParser import ConfigParser

import redcap
reload(redcap)

study = 'Testing'

config = ConfigParser()
config.read([os.path.expanduser('~/.pycap.cfg')])
API_Key = config.get('keys', study)

url = 'https://redcap.vanderbilt.edu/api/'

project = redcap.Project(url, API_Key)

#Data to import
data = [{'study_id':'1',
        'first_name':'John',
        'last_name':'Doe',
        'dob':'2000-01-01',
        'sex':'1',
        'foo_score':'1',
        'bar_score':'2',
        'image_path':'/path/to/image',
        'address':'123 Main Street, Anytown USA 23456',
        'phone_number':6155551234},
        {'study_id':'2',
        'first_name':'Jane',
        'last_name':'Smith',
        'dob':'2000-02-01',
        'sex':'0',
        'foo_score':'10',
        'bar_score':'20',
        'image_path':'/path/to/image2',
        'address':'124 Main Street, Anytown USA 12345',
        'phone_number':6155556789}]

num_imports = project.import_records(data)
