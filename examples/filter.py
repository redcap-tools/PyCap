#!/usr/bin/env python

"""
Copyright (c) 2011, Scott Burns
All rights reserved.
"""

import sys
import os

from redcap import rc
reload(rc)

USE_YAML = True

"""
You need to somehow bring your API keys into python.

I have them written in a yaml document at ~/.pycap.yaml and it looks like this:

KEYS:
    {study_name}: {API KEY}
    {study_name}: {API KEY}
    {study_name}: {API KEY}
    {study_name}: {API KEY}

You can put them straight into this (or another file), but be wary of including
your sensitive data (the API keys) in version-control systems.
"""
if USE_YAML:
    import yaml
    pycap_path = os.path.expanduser('~/.pycap.yaml')
    try:
        with open(pycap_path, 'r') as f:
            rc_data = yaml.load(f)
    except IOError:
        print("Cannot load pycap user data")
        rc_data = {}

# $ python pycap {study_name}
study = sys.argv[1]

if ('KEYS' not in rc_data) or (study not in rc_data['KEYS']):
    raise ValueError('%s API key not found in %s' % (study, pycap_path))

# If you just want to copy/paste your API key, here's the place
API_Key = rc_data['KEYS'][study]

vandy_url = "https://redcap.vanderbilt.edu/api/"

# We instantiate a RedCap project with your REDCap URL and API Key 
project = rc.RCProject(vandy_url, API_Key)

"""The following query is project specific because every project will have 
different field_names (aka keys, headers, etc.)

If you want to find all of the field_names and their associated labels, you can
do this in code:

project.names_labels(do_print=True)

This will print many lines of {field_name} --> {field_label}

where field_name is a specific column name as known to the REDCap database and 
field_label is a (hopefully) more verbose description string.

It is the field_names that should be used when building Query/QueryGroup 
objects.
"""

# q1 = rc.Query('subjage', {'le':12, 'ge':8}, 'number')
# q2 = rc.Query('wjbrsss', {'ge':75},'number')
# q3 = rc.Query('wiscfsiq', {'ge': 100}, 'number')
# 
# 
# query_group = rc.QueryGroup(q1)
# query_group.add_query(q2, 'AND')
# query_group.add_query(q3) # AND is the default logic, but OR is available too
# group = project.filter(query_group)
