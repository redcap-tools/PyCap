"""Test fixtures for unit tests only"""
# pylint: disable=redefined-outer-name
import json
import urllib.parse as urlparse

import pytest
import responses

from redcap import Project

# pylint: disable=too-many-branches


@pytest.fixture(scope="module")
def project_token() -> str:
    """Project API token"""
    return "supersecrettoken"


@pytest.fixture(scope="module")
def project_urls() -> dict[str]:
    """Different urls for different mock projects"""
    return {
        "bad_url": "https://redcap.badproject.edu/api",
        "long_project": "https://redcap.longproject.edu/api/",
        "simple_project": "https://redcap.simpleproject.edu/api/",
        "ssl_project": "https://redcap.sslproject.edu/api/",
        "survey_project": "https://redcap.surveyproject.edu/api/",
    }


# See here for docs: https://github.com/getsentry/responses#responses-as-a-pytest-fixture
@pytest.fixture(scope="module")
def mocked_responses() -> responses.RequestsMock:
    """Base fixture for all mocked responses"""
    with responses.RequestsMock() as resps:
        yield resps


@pytest.fixture(scope="module")
def simple_project(project_urls, project_token, mocked_responses) -> Project:
    """Mocked simple REDCap project"""

    def request_callback_simple(req) -> None:
        parsed = urlparse.urlparse(f"?{req.body}")
        data = urlparse.parse_qs(parsed.query)
        headers = {"Content-Type": "application/json"}

        resp = None
        if " filename" in data:
            resp = {}
        else:
            request_type = data.get("content", ["unknown"])[0]

            if "returnContent" in data:
                if "non_existent_key" in data["data"][0]:
                    resp = {"error": "invalid field"}
                else:
                    resp = {"count": 1}
            elif request_type == "metadata":
                # importing metadata
                if "data" in data:
                    data_len = len(json.loads(data["data"][0]))
                    resp = json.dumps(data_len)
                    return (201, headers, resp)
                # exporting metadata
                if "csv" in data["format"]:
                    resp = (
                        "field_name,field_label,form_name,arm_num,name\n"
                        "record_id,Record ID,Test Form,1,test\n"
                    )
                    headers = {"content-type": "text/csv; charset=utf-8"}
                    return (201, headers, resp)

                resp = [
                    {
                        "field_name": "record_id",
                        "field_label": "Record ID",
                        "form_name": "Test Form",
                        "arm_num": 1,
                        "name": "test",
                        "field_type": "text",
                    },
                    {
                        "field_name": "file",
                        "field_label": "File",
                        "form_name": "Test Form",
                        "arm_num": 1,
                        "name": "file",
                        "field_type": "file",
                    },
                    {
                        "field_name": "dob",
                        "field_label": "Date of Birth",
                        "form_name": "Test Form",
                        "arm_num": 1,
                        "name": "dob",
                        "field_type": "date",
                    },
                ]
            elif request_type == "version":
                resp = {"error": "no version info"}
            elif request_type == "event":
                resp = {"error": "no events"}
            elif request_type == "arm":
                resp = {"error": "no arm"}
            elif request_type == "record":
                if "csv" in data["format"]:
                    resp = "record_id,test,first_name,study_id\n1,1,Peter,1"
                    headers = {"content-type": "text/csv; charset=utf-8"}
                    return (201, headers, resp)

                if "exportDataAccessGroups" in data:
                    resp = [
                        {
                            "field_name": "record_id",
                            "redcap_data_access_group": "group1",
                        },
                        {
                            "field_name": "test",
                            "redcap_data_access_group": "group1",
                        },
                    ]
                elif "label" in data.get("rawOrLabel"):
                    resp = [{"matcheck1___1": "Foo"}]
                else:
                    resp = [
                        {"record_id": "1", "test": "test1"},
                        {"record_id": "2", "test": "test"},
                    ]
            elif request_type == "file":
                resp = {}
                headers["content-type"] = "text/plain;name=data.txt"
            elif request_type == "user":
                resp = [
                    {
                        "firstname": "test",
                        "lastname": "test",
                        "email": "test",
                        "username": "test",
                        "expiration": "test",
                        "data_access_group": "test",
                        "data_export": "test",
                        "forms": "test",
                    }
                ]
            elif request_type == "generateNextRecordName":
                resp = 123
            elif request_type == "project":
                resp = {"project_id": 123}

            assert resp is not None, f"No response for {request_type=}"

        return (201, headers, json.dumps(resp))

    simple_project_url = project_urls["simple_project"]
    mocked_responses.add_callback(
        responses.POST,
        simple_project_url,
        callback=request_callback_simple,
        content_type="application/json",
    )

    return Project(simple_project_url, project_token)
