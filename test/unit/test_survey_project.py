#! /usr/bin/env python
"""Test suite for Project class against mocked REDCap server"""
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
from test.unit.callback_utils import get_survey_project_request_handler, parse_request

import pytest
import responses

from redcap import Project


@pytest.fixture(scope="module")
def survey_project(project_urls, project_token, mocked_responses) -> Project:
    """Mocked simple REDCap project, with survey fields"""

    def request_callback_survey(req):
        request_data, request_headers, request_type = parse_request(req)
        request_handler = get_survey_project_request_handler(request_type)
        response = request_handler(data=request_data, headers=request_headers)
        return response

    survey_project_url = project_urls["survey_project"]
    mocked_responses.add_callback(
        responses.POST,
        survey_project_url,
        callback=request_callback_survey,
        content_type="application/json",
    )

    return Project(survey_project_url, project_token, verify_ssl=False)


def test_init(survey_project):
    assert isinstance(survey_project, Project)


def test_export_survey_fields(survey_project):
    records = survey_project.export_records(export_survey_fields=True)

    for record in records:
        assert "redcap_survey_identifier" in record
        assert "demographics_timestamp" in record
