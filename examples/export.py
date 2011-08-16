#!/usr/bin/env python

"""
Copyright (c) 2011, Scott Burns
All rights reserved.
"""
import os
import sys
import redcap as rc
reload(rc)

# $ python export.py {study_name}
study = sys.argv[1]


############################
## BEGIN API KEY BOILERPLATE
USE_YAML = True

"""
You need to somehow bring your API keys into python.

I have them written in a yaml document at ~/.pycap.yaml and it looks like this:

KEYS:
    {study_name}: {API KEY}
    {study_name}: {API KEY}
    {study_name}: {API KEY}
    {study_name}: {API KEY}

You can put them straight into this code (or another file), but be wary of 
including your API keys in version-control systems.
"""
import yaml
pycap_path = os.path.expanduser('~/.pycap.yaml')
try:
    with open(pycap_path, 'r') as f:
        rc_data = yaml.load(f)
except IOError:
    print("Cannot load pycap user data")
    rc_data = {}

if ('KEYS' not in rc_data) or (study not in rc_data['KEYS']):
    raise ValueError('%s API key not found in %s' % (study, pycap_path))
## END API KEY BOILERPLATE
##########################

API_Key = rc_data['KEYS'][study]

vandy_url = "https://redcap.vanderbilt.edu/api/"

project = rc.Project(vandy_url, API_Key)

field_names = project.field_names

# grab a subset of your data set
data = project.export_records(fields=field_names[:5])
