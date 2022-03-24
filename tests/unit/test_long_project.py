#! /usr/bin/env python
"""Test suite for Project class, with long project, against mocked REDCap server"""
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
import os

import pandas as pd
import pytest
import responses

from redcap import Project, RedcapError
from tests.unit.callback_utils import (
    is_json,
    get_long_project_request_handler,
    parse_request,
)


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


def test_file_import(long_project):
    this_dir, _ = os.path.split(__file__)
    upload_fname = os.path.join(this_dir, "data.txt")
    with open(upload_fname, "r", encoding="UTF-8") as fobj:
        content = long_project.import_file(
            "1", "file", upload_fname, fobj, event="raw", repeat_instance=1
        )

    assert content == [{}]


def test_file_delete(long_project):
    record, field = "1", "file"
    content = long_project.delete_file(record, field, event="raw")
    assert content == [{}]


def test_export_survey_participants_list(long_project):
    res = long_project.export_survey_participant_list(instrument="test", event="raw")

    assert is_json(res)


def test_metadata_import_handles_api_error(long_project):
    metadata = long_project.export_metadata()

    with pytest.raises(RedcapError):
        long_project.import_metadata(metadata)


def test_is_longitudinal(long_project):
    assert long_project.is_longitudinal


def test_export_with_events(long_project):
    events = long_project.export_instrument_event_mappings()
    unique_event = events[0]["unique_event_name"]
    data = long_project.export_records(events=[unique_event])

    assert isinstance(data, list)

    for record in data:
        assert isinstance(record, dict)


def test_fem_export(long_project):
    fem = long_project.export_instrument_event_mappings(format_type="json")

    assert isinstance(fem, list)

    for arm in fem:
        assert isinstance(arm, dict)


def test_fem_export_stricly_enforces_format(long_project):
    with pytest.raises(ValueError):
        long_project.export_instrument_event_mappings(format_type="unsupported")


def test_export_to_df_gives_multi_index(long_project):
    long_dataframe = long_project.export_records(format_type="df", event_name="raw")

    assert hasattr(long_dataframe.index, "names")


def test_import_dataframe(long_project):
    long_dataframe = long_project.export_records(event_name="raw", format_type="df")
    response = long_project.import_records(long_dataframe, import_format="df")

    assert "count" in response
    assert "error" not in response


def test_reports_df_export(long_project):
    report = long_project.export_report(report_id="1", format_type="df")

    assert isinstance(report, pd.DataFrame)


def test_repeating_export(long_project):
    rep = long_project.export_repeating_instruments_events(format_type="json")

    assert isinstance(rep, list)


def test_import_export_repeating_forms(long_project):
    rep = long_project.export_repeating_instruments_events(format_type="json")
    res = long_project.import_repeating_instruments_events(
        to_import=rep, import_format="json"
    )
    assert res == 1
