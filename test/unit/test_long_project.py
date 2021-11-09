#! /usr/bin/env python
"""Test suite for Project class, with long project, against mocked REDCap server"""
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
from test.unit.callback_utils import get_long_project_request_handler, parse_request

import pytest
import responses

from redcap import Project, RedcapError


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


def test_file_export(long_project):
    record, field = "1", "file"
    content, _ = long_project.export_file(record, field, event="raw", repeat_instance=1)
    assert isinstance(content, bytes)


def test_metadata_import_handles_api_error(long_project):
    metadata = long_project.export_metadata()

    with pytest.raises(RedcapError):
        long_project.import_metadata(metadata)


def test_long_attrs_are_populated(long_project):
    assert long_project.events is not None
    assert long_project.arm_names is not None
    assert long_project.arm_nums is not None


def test_is_longitudinal(long_project):
    assert long_project.is_longitudinal()


def test_export_with_events(long_project):
    unique_event = long_project.events[0]["unique_event_name"]
    data = long_project.export_records(events=[unique_event])

    assert isinstance(data, list)

    for record in data:
        assert isinstance(record, dict)


def test_fem_export(long_project):
    fem = long_project.export_fem(format="json")

    assert isinstance(fem, list)

    for arm in fem:
        assert isinstance(arm, dict)


def test_fem_export_stricly_enforces_format(long_project):
    with pytest.raises(ValueError):
        long_project.export_fem(format="unsupported")


def test_export_to_df_gives_multi_index(long_project):
    long_dataframe = long_project.export_records(format="df", event_name="raw")

    assert hasattr(long_dataframe.index, "names")


def test_import_dataframe(long_project):
    long_dataframe = long_project.export_records(event_name="raw", format="df")
    response = long_project.import_records(long_dataframe)

    assert "count" in response
    assert "error" not in response
