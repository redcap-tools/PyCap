#!/usr/bin/env python

"""
Copyright (c) 2011, Scott Burns
All rights reserved.
"""
import os
import sys
import redcap as rc
reload(rc)

from ConfigParser import ConfigParser

# $ python export.py {study_name}
study = sys.argv[1]

# Use a .cfg file to store API keys
config = ConfigParser()
config.read([os.path.expanduser('~/.pycap.cfg')])
API_Key = config.get('keys', study)

vandy_url = "https://redcap.vanderbilt.edu/api/"

project = rc.Project(vandy_url, API_Key)

field_names = project.field_names

# grab a subset of your data set
data = project.export_records(fields=field_names[:5])
