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


def test_instruments_export(long_project):
    response = long_project.export_instruments()

    assert len(response) == 3


def test_pdf_export(long_project):
    content, _ = long_project.export_pdf()

    assert isinstance(content, bytes)


def test_pdf_export_specify(long_project):
    content, _ = long_project.export_pdf(
        record="1", event="raw", instrument="test", repeat_instance=1
    )

    assert isinstance(content, bytes)


def test_pdf_export_all_records(long_project):
    content, _ = long_project.export_pdf(all_records=True)

    assert isinstance(content, bytes)


def test_pdf_export_compact_display(long_project):
    content, _ = long_project.export_pdf(compact_display=True)

    assert isinstance(content, bytes)


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

    assert len(fem) == 1


def test_fem_export_stricly_enforces_format(long_project):
    with pytest.raises(ValueError):
        long_project.export_instrument_event_mappings(format_type="unsupported")


def test_fem_import(long_project):
    instrument_event_mappings = [
        {"arm_num": "1", "unique_event_name": "event_1_arm_1", "form": "form_2"}
    ]
    res = long_project.import_instrument_event_mappings(instrument_event_mappings)

    assert res == 1


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


def test_arms_export(long_project):
    response = long_project.export_arms()

    assert len(response) == 1


def test_arms_import(long_project):
    new_arms = [{"arm_num": 2, "name": "test_2"}]
    response = long_project.import_arms(new_arms)

    assert response == 1


def test_arms_export_specify_arm(long_project):
    response = long_project.export_arms(arms=[2])

    assert len(response) == 1

    assert any(arm["name"] == "test_2" for arm in response)


def test_arms_import_override(long_project):
    new_arms = [{"arm_num": 3, "name": "test_3"}, {"arm_num": 4, "name": "test_4"}]
    response = long_project.import_arms(new_arms, override=1)

    assert response == 2


def test_arms_delete(long_project):
    arms = [3]
    response = long_project.delete_arms(arms)

    assert response == 1


def test_events_export(long_project):
    response = long_project.export_events()

    assert len(response) == 1


def test_events_import(long_project):
    new_events = [{"event_name": "Event 2", "arm_num": "1"}]
    response = long_project.import_events(new_events)

    assert response == 1


def test_events_export_specify_arm(long_project):
    response = long_project.export_events(arms=[1])

    assert len(response) == 2

    assert any(event["arm_num"] == 1 for event in response)


def test_events_import_override(long_project):
    new_events = [
        {"event_name": "Event 3", "arm_num": "1"},
        {"event_name": "Event 4", "arm_num": "1"},
    ]
    response = long_project.import_events(new_events, override=1)

    assert response == 2


def test_events_delete(long_project):
    events = ["event_4_arm_1"]
    response = long_project.delete_events(events)

    assert response == 1


def test_file_repo_folder_create(long_project):
    response = long_project.create_folder_in_repository(
        name="test", folder_id=1, dag_id=2, role_id=3
    )
    assert response[0]["folder_id"]
