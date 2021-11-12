"""Test fixtures for integration tests only"""
# pylint: disable=redefined-outer-name
from datetime import datetime
import os

import pytest
import requests

from redcap import Project


@pytest.fixture(scope="module")
def redcapdemo_url():
    """API url for redcapdemo testing site"""
    return "https://redcapdemo.vanderbilt.edu/api/"


@pytest.fixture(scope="module")
def simple_project_token(redcapdemo_url):
    """Create a simple project for testing on redcapdemo.vanderbilt.edu
    This API method returns the token for the newly created project, which
    is passed to the simple project tests
    """
    super_token = os.getenv("REDCAPDEMO_SUPERUSER_TOKEN")
    current_time = datetime.now().strftime("%m-%d %H:%M:%S")
    project_title = f"PyCap Test Simple Project: {current_time}"
    project_info = f"""<?xml version="1.0" encoding="UTF-8" ?>
    <item>
    <project_title>{project_title}</project_title>
    <purpose>0</purpose>
    </item>"""

    with open("tests/data/test_simple_project.xml", encoding="UTF-8") as proj_xml_file:
        project_data = proj_xml_file.read()

    res = requests.post(
        url=redcapdemo_url,
        data={
            "token": super_token,
            "content": "project",
            "format": "xml",
            "data": project_info,
            "odm": project_data,
        },
    )

    return res.text


@pytest.fixture(scope="module")
def simple_project(redcapdemo_url, simple_project_token):
    """A simple REDCap project"""
    return Project(redcapdemo_url, simple_project_token)
