"""Programtically create projects for testing purposes"""
import os

import requests

SUPER_TOKEN = os.getenv("REDCAPDEMO_SUPERUSER_TOKEN")

PROJECT_INFO = """<?xml version="1.0" encoding="UTF-8" ?>
<item>
   <project_title>PyCap Test Simple Project</project_title>
   <purpose>0</purpose>
</item>"""

with open("scripts/test_simple_project.xml") as proj_xml_file:
    PROJECT_DATA = proj_xml_file.read()

res = requests.post(
    url="https://redcapdemo.vanderbilt.edu/api/",
    data={
        "token": SUPER_TOKEN,
        "content": "project",
        "format": "xml",
        "data": PROJECT_INFO,
        "odm": PROJECT_DATA,
    },
)

print("HTTP Status: " + str(res.status_code))
# Right now, this will change whenever the project needs to be re-created
# this could be reason enough to create a fresh project on _every_ test run
# knowing that they will get wiped weekly. And the REDCap team will reach out if they
# have any issues with how often we're hitting the API
NEW_TOKEN = res.text
print(NEW_TOKEN)
