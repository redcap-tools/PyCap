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

q1 = rc.Query('subjage', {'le':12, 'ge':8}, 'number')
q2 = rc.Query('wjbrsss', {'ge':75},'number')

match1 = project.single_filter(q1)
match2 = project.single_filter(q2)
print("Manually made...")
man = sorted(set(match1) & set(match2))
print(man)
print(len(man))

query_group = rc.QueryGroup(q1)
query_group.add_query(q2, 'AND')
auto = project.group_filter(query_group)
print("Made with QueryGroup")
print(sorted(auto))
print(len(auto))



# q1 = rc.Query('score', {'ge':12})
# q2 = rc.Query('index', {'ge':75})
# q3 = rc.Query('cat', {'eq':'RD'}, 'string')
# 
# qg = rc.QueryGroup(q1)
# qg.add_query(q2)
# qg.add_query(q3)
# 
# 
# q5 = rc.Query('iq', {'ge':85})
# q6 = rc.Query('subscore', {'ge':74})
# 
# qg2 = rc.QueryGroup(q5)
# qg2.add_query(q6, 'OR')
# 
# qg.add_query(qg2, 'OR')
# 
# print qg
# 
# print qg.fields()

