#!/usr/bin/env python

"""
Copyright (c) 2011, Scott Burns
All rights reserved.
"""

import sys
import os

from redcap import rc
reload(rc)

# $ python pycap {study_name}
study = sys.argv[1]

############################
## BEGIN API KEY BOILERPLATE

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
pycap_path = os.path.expanduser('~/.pycap.yml')
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


# If you just want to copy/paste your API key, here's the place
API_Key = rc_data['KEYS'][study]

vandy_url = "https://redcap.vanderbilt.edu/api/"

# We instantiate a RedCap project with your REDCap URL and API Key 
project = rc.Project(vandy_url, API_Key)

q1 = rc.Query('subjage', {'le':12, 'ge':8}, 'number')
q2 = rc.Query('wjbrsss', {'ge':75},'number')
q3 = rc.Query('wiscfsiq', {'ge': 100}, 'number')

query_group = rc.QueryGroup(q1)
query_group.add_query(q2, 'AND')
query_group.add_query(q3) # AND is the default logic, but OR is available too
group = project.filter(query_group)
