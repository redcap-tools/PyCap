#!/usr/bin/env python

"""
Copyright (c) 2011, Scott Burns
All rights reserved.
"""

import sys
import os

from redcap import rc
reload(rc)

study = 'NF1'

config = ConfigParser()
with open(os.path.expanduser('~/.pycap.cfg')) as f:
    config.readfp(f)    
API_Key = config.get('keys', study)


vandy_url = "https://redcap.vanderbilt.edu/api/"

# We instantiate a RedCap project with your REDCap URL and API Key 
project = rc.Project(vandy_url, API_Key)

# These fields are known to be in the study specified above
q1 = rc.Query('subjage', {'le':12, 'ge':8}, 'number')
q2 = rc.Query('wjbrsss', {'ge':75},'number')
q3 = rc.Query('wiscfsiq', {'ge': 100}, 'number')

query_group = rc.QueryGroup(q1)
query_group.add_query(q2, 'AND')
query_group.add_query(q3) # AND is the default logic, but OR is available too
group = project.filter(query_group)
