"""Test fixtures for integration tests only"""
# pylint: disable=redefined-outer-name
from datetime import datetime
import os

from pathlib import Path

import pytest
import requests

from redcap import Project

SUPER_TOKEN = os.getenv("REDCAPDEMO_SUPERUSER_TOKEN")


def create_project(url: str, super_token: str, project_xml_path: Path) -> str:
    """Create a project for testing on redcapdemo.vanderbilt.edu
    This API method returns the token for the newly created project, which
    used for the integration tests
    """
    current_time = datetime.now().strftime("%m-%d %H:%M:%S")
    project_title = f"PyCap { project_xml_path.stem }: { current_time }"
    project_info = f"""<?xml version="1.0" encoding="UTF-8" ?>
    <item>
    <project_title>{project_title}</project_title>
    <purpose>0</purpose>
    </item>"""

    with open(project_xml_path, encoding="UTF-8") as proj_xml_file:
        project_data = proj_xml_file.read()

    res = requests.post(
        url=url,
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
def redcapdemo_url() -> str:
    """API url for redcapdemo testing site"""
    return "https://redcapdemo.vanderbilt.edu/api/"


@pytest.fixture(scope="module")
def simple_project_token(redcapdemo_url) -> str:
    """Create a simple project and return it's API token"""
    simple_project_xml_path = Path("tests/data/test_simple_project.xml")
    project_token = create_project(redcapdemo_url, SUPER_TOKEN, simple_project_xml_path)

    return project_token


@pytest.fixture(scope="module")
def simple_project(redcapdemo_url, simple_project_token):
    """A simple REDCap project"""
    return Project(redcapdemo_url, simple_project_token)


@pytest.fixture(scope="module")
def long_project_token(redcapdemo_url) -> str:
    """Create a long project and return it's API token"""
    long_project_xml_path = Path("tests/data/test_long_project.xml")
    project_token = create_project(redcapdemo_url, SUPER_TOKEN, long_project_xml_path)

    return project_token


@pytest.fixture(scope="module")
def long_project(redcapdemo_url, long_project_token):
    """A long REDCap project"""
    return Project(redcapdemo_url, long_project_token)
