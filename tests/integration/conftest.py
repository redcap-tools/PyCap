"""Test fixtures for integration tests only"""

# pylint: disable=redefined-outer-name
import os
import tempfile

from datetime import datetime
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


def add_files_to_repository(proj: Project) -> Project:
    """Given a project, fill out it's file repository
    For some reason, this doesn't carry over in the XML file so
    it has to be done after project creation
    """
    new_folder = proj.create_folder_in_repository("test").pop()

    # pylint: disable=consider-using-with
    # Can't figure out how to do this in a cleaner way
    tmp_file = tempfile.NamedTemporaryFile()
    # pylint: enable=consider-using-with
    with open(tmp_file.name, mode="w", encoding="utf-8") as tmp:
        tmp.write("hello")

    proj.import_file_into_repository(file_name="test.txt", file_object=tmp_file)
    proj.import_file_into_repository(
        file_name="test_in_folder.txt",
        file_object=tmp_file,
        folder_id=new_folder["folder_id"],
    )

    return proj


@pytest.fixture(scope="module")
def simple_project(redcapdemo_url_fixture, simple_project_token):
    """A simple REDCap project"""
    simple_proj = Project(redcapdemo_url_fixture, simple_project_token)
    simple_proj = grant_superuser_rights(simple_proj)
    simple_proj = add_files_to_repository(simple_proj)

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
