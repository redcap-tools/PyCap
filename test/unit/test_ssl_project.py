#! /usr/bin/env python
"""Test suite for Project class against mocked REDCap server without ssl verification"""
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
from test.unit.callback_utils import get_simple_project_request_handler, parse_request

import pytest
import responses

from redcap import Project


@pytest.fixture(scope="module")
def ssl_project(project_urls, project_token, mocked_responses) -> Project:
    """Mocked simple REDCap project, without verified ssl"""

    def request_callback_simple(req):
        request_data, request_headers, request_type = parse_request(req)
        request_handler = get_simple_project_request_handler(request_type)
        response = request_handler(data=request_data, headers=request_headers)
        return response

    ssl_project_url = project_urls["ssl_project"]
    mocked_responses.add_callback(
        responses.POST,
        ssl_project_url,
        callback=request_callback_simple,
        content_type="application/json",
    )

    return Project(ssl_project_url, project_token, verify_ssl=False)


def test_init(ssl_project):
    assert isinstance(ssl_project, Project)


# pylint: disable=protected-access
def test_verify_ssl_can_be_disabled(ssl_project):
    post_kwargs = ssl_project._kwargs()
    assert "verify" in post_kwargs
    assert not post_kwargs["verify"]


# pylint: enable=protected-access
