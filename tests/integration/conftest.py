"""Test fixtures for integration tests only"""

# pylint: disable=redefined-outer-name
from datetime import datetime
import os

from pathlib import Path
from typing import cast

import pytest
import requests

from redcap import Project

SUPER_TOKEN = os.getenv("REDCAPDEMO_SUPERUSER_TOKEN")


def create_project(url: str, super_token: str, project_xml_path: Path) -> str:
    """Create a project for testing on redcapdemo.vumc.org
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
        timeout=60,
    )
    # Response includes a bunch of SQL statements before we get to the token
    # This limits the return value to just the token
    return res.text[-32:]


def redcapdemo_url() -> str:
    """API url for redcapdemo testing site"""
    return "https://redcapdemo.vumc.org/api/"


@pytest.fixture(scope="module")
def redcapdemo_url_fixture() -> str:
    """API url for redcapdemo testing site, as a testing fixture"""
    return redcapdemo_url()


@pytest.fixture(scope="module")
def simple_project_token(redcapdemo_url_fixture) -> str:
    """Create a simple project and return it's API token"""
    simple_project_xml_path = Path("tests/data/test_simple_project.xml")
    super_token = cast(str, SUPER_TOKEN)
    project_token = create_project(  # type: ignore
        redcapdemo_url_fixture, super_token, simple_project_xml_path
    )

    return project_token


def grant_superuser_rights(proj: Project) -> Project:
    """Given a newly created project, give the superuser
    the highest level of user rights
    """
    superuser = proj.export_users()[0]

    superuser["record_delete"] = 1
    superuser["record_rename"] = 1
    superuser["lock_records_all_forms"] = 1
    superuser["lock_records"] = 1

    res = proj.import_users([superuser])
    assert res == 1

    return proj


@pytest.fixture(scope="module")
def simple_project(redcapdemo_url_fixture, simple_project_token):
    """A simple REDCap project"""
    simple_proj = Project(redcapdemo_url_fixture, simple_project_token)
    simple_proj = grant_superuser_rights(simple_proj)
    # Import attributes that aren't saved in the xml file
    simple_proj.create_folder_in_repository("test")
    return simple_proj


@pytest.fixture(scope="module")
def long_project_token(redcapdemo_url_fixture) -> str:
    """Create a long project and return it's API token"""
    long_project_xml_path = Path("tests/data/test_long_project.xml")
    super_token = cast(str, SUPER_TOKEN)
    project_token = create_project(
        redcapdemo_url_fixture, super_token, long_project_xml_path
    )

    return project_token


@pytest.fixture(scope="module")
def long_project(redcapdemo_url_fixture, long_project_token):
    """A long REDCap project"""
    long_proj = Project(redcapdemo_url_fixture, long_project_token)
    long_proj = grant_superuser_rights(long_proj)
    return long_proj
