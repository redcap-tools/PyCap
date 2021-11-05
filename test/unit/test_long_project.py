#! /usr/bin/env python
"""Test suite for Project class against mocked REDCap server"""
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
import os

from io import StringIO

from test.unit.callback_utils import get_long_project_request_handler, parse_request

import pandas as pd
import pytest
import responses

from redcap import Project


@pytest.fixture(scope="module")
def long_project(project_urls, project_token, mocked_responses) -> Project:
    """Mocked simple REDCap project"""

    def request_callback_long(req):
        request_data, request_headers, request_type = parse_request(req)
        request_handler = get_long_project_request_handler(request_type)
        response = request_handler(data=request_data, headers=request_headers)
        return response

    long_project_url = project_urls["long_project"]
    mocked_responses.add_callback(
        responses.POST,
        long_project_url,
        callback=request_callback_long,
        content_type="application/json",
    )

    return Project(long_project_url, project_token)


def test_init(long_project):
    assert isinstance(long_project, Project)
