#!/usr/bin/env python

"""
Copyright (c) 2011, Scott Burns
All rights reserved.
"""

import sys
import os
import yaml

from redcap import rc
reload(rc)


pycap_path = os.path.expanduser('~/.pycap.yaml')
try:
    with open(pycap_path, 'r') as f:
        rc_data = yaml.load(f)
except IOError:
    print("Cannot load pycap user data")
    rc_data = {}

study = sys.argv[1]

if ('KEYS' not in rc_data) or (study not in rc_data['KEYS']):
    raise ValueError('%s API key not found in %s' % (study, pycap_path))

project = rc.RCProject(rc_data['KEYS'][study], study)


query = rc.Query('subjage', [{'le':10}], 'number')
good = project.single_filter(query)


q1 = rc.Query('cat', [{'ge':12}])
q2 = rc.Query('ind', [{'ge':12}])
q3 = rc.Query('wjwa', [{'ge':12}])
q4 = rc.Query('wjlid', [{'ge':12}])

qg = rc.QueryGroup(q1)
qg.add_query(q2)
qg.add_query(q3)
qg.add_query(q4)


q5 = rc.Query('cat', [{'ge':12}])
q6 = rc.Query('ind', [{'ge':12}])

qg2 = rc.QueryGroup(q5)
qg2.add_query(q6, 'OR')

qg.add_query(qg2, 'OR')

print qg
