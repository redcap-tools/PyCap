#! /usr/bin/env python
"""Test suite for Project class against mocked REDCap server"""
# pylint: disable=missing-function-docstring
# pylint: disable=redefined-outer-name
import os

from datetime import datetime
from io import StringIO


import pandas as pd
import pytest
import responses
import semantic_version

from redcap import Project, RedcapError
from tests.unit.callback_utils import (
    is_json,
    get_simple_project_request_handler,
    parse_request,
)


@pytest.fixture(scope="module")
def simple_project(project_urls, project_token, mocked_responses) -> Project:
    """Mocked simple REDCap project"""

    def request_callback_simple(req):
        request_data, request_headers, request_type = parse_request(req)
        request_handler = get_simple_project_request_handler(request_type)
        response = request_handler(data=request_data, headers=request_headers)
        return response

    simple_project_url = project_urls["simple_project"]
    mocked_responses.add_callback(
        responses.POST,
        simple_project_url,
        callback=request_callback_simple,
        content_type="application/json",
    )

    return Project(simple_project_url, project_token)


def test_bad_creds(project_urls, project_token):
    # this url is "bad" because we didn't set up an response fixture for it
    bad_url = project_urls["bad_url"]

    with pytest.raises(RedcapError):
        Project(bad_url, project_token)
    with pytest.raises(RedcapError):
        Project(bad_url, "1")


def test_init(simple_project):
    assert isinstance(simple_project, Project)


def test_filter_metadata_enforces_strict_keys(simple_project):
    with pytest.raises(KeyError):
        simple_project.filter_metadata("fake_column")


def test_metadata_type_catches_non_existent_fields(simple_project, capsys):
    res = simple_project.metadata_type("fake_field")
    out, _ = capsys.readouterr()

    assert res == ""
    assert "not in metadata field:fake_field" in out


# pylint: disable=protected-access
def test_verify_ssl_defaults_to_true(simple_project):
    post_kwargs = simple_project._kwargs()
    assert "verify" in post_kwargs
    assert post_kwargs["verify"]


# pylint: enable=protected-access


def test_server_error_produces_redcap_error(simple_project):
    # trigger the "server error" test with the "server_error" field
    with pytest.raises(RedcapError):
        simple_project.export_records(filter_logic=["server_error"])


def test_bad_request_produces_redcap_error(simple_project):
    with pytest.raises(RedcapError):
        simple_project.export_records(filter_logic=["bad_request"])


def test_get_version(simple_project):
    assert simple_project.redcap_version == semantic_version.Version("11.2.3")


def test_life_goes_on_without_the_version(simple_project, mocker):
    mocker.patch.object(simple_project, "_Project__rcv", side_effect=(Exception))

    with pytest.raises(RedcapError):
        simple_project.configure()


def test_attrs(simple_project):
    for attr in (
        "metadata",
        "field_names",
        "field_labels",
        "forms",
        "events",
        "arm_names",
        "arm_nums",
        "def_field",
    ):
        assert hasattr(simple_project, attr)


def test_is_not_longitudinal(simple_project):
    assert not simple_project.is_longitudinal()


def test_events_and_arms_attrs_are_empty(simple_project):
    for attr in "events", "arm_names", "arm_nums":
        attr_obj = getattr(simple_project, attr)
        assert attr_obj == ()


# Right now it seems like this isn't acutally testing the date formatting?
# just passing through a bogus option still passes the test. Consider modifying method
# to strictly enforce these options, or removing this test.
@pytest.mark.parametrize(
    "record, date_format",
    [
        ([{"study_id": "1", "dob": "2000-01-01"}], "YMD"),
        ([{"study_id": "1", "dob": "31/01/2000"}], "DMY"),
        ([{"study_id": "1", "dob": "12/31/2000"}], "MDY"),
    ],
)
def test_import_date_formatting(simple_project, record, date_format):
    response = simple_project.import_records(record, date_format=date_format)

    assert response["count"] == 1


def test_file_import(simple_project):
    this_dir, _ = os.path.split(__file__)
    upload_fname = os.path.join(this_dir, "data.txt")
    with open(upload_fname, "r", encoding="UTF-8") as fobj:
        simple_project.import_file("1", "file", upload_fname, fobj)


def test_file_export(simple_project):
    record, field = "1", "file"
    content, headers = simple_project.export_file(record, field)
    assert isinstance(content, bytes)
    # We should at least get the filename in the headers
    assert "name" in headers
    # needs to raise ValueError for exporting non-file fields
    with pytest.raises(ValueError):
        simple_project.export_file(record=record, field="dob")


def test_user_export(simple_project):
    users = simple_project.export_users()
    # A project must have at least one user
    assert len(users) > 0

    req_keys = [
        "firstname",
        "lastname",
        "email",
        "username",
        "expiration",
        "data_access_group",
        "data_export",
        "forms",
    ]
    for user in users:
        for key in req_keys:
            assert key in user


def test_generate_next_record_name(simple_project):
    next_name = simple_project.generate_next_record_name()

    assert next_name == 123


def test_delete_records(simple_project):
    response = simple_project.delete_records([1, 2, 3])

    assert response == "3"


def test_delete_records_passes_filters_as_arrays(simple_project, mocker):
    mocked_api_call = mocker.patch.object(
        simple_project, "_call_api", return_value=(None, None)
    )

    simple_project.delete_records([1, 2])

    args, _ = mocked_api_call.call_args

    payload = args[0]

    assert payload["records[0]"] == 1
    assert payload["records[1]"] == 2


def test_export_field_names(simple_project):
    export_field_names = simple_project.export_field_names()

    assert is_json(export_field_names)


def test_export_df_field_names_single_field(simple_project):
    export_field_name = simple_project.export_field_names(format="df", field="test")

    assert isinstance(export_field_name, pd.DataFrame)
    assert len(export_field_name) == 1


def test_export_field_names_strictly_enforces_format(simple_project):
    with pytest.raises(ValueError):
        simple_project.export_field_names(format="unsupported")


def test_export_project_info(simple_project):
    info = simple_project.export_project_info()

    assert info["project_id"] == 123


def test_metadata_csv_export(simple_project):
    metadata_csv_export = simple_project.export_metadata(format="csv")
    data = pd.read_csv(StringIO(metadata_csv_export))

    assert len(data) == 1


def test_metadata_df_export(simple_project):
    dataframe = simple_project.export_metadata(format="df")

    assert isinstance(dataframe, pd.DataFrame)


def test_metadata_df_export_correctly_uses_df_kwargs(simple_project):
    dataframe = simple_project.export_metadata(
        format="df", df_kwargs={"index_col": "field_label"}
    )
    assert dataframe.index.name == "field_label"
    assert "field_name" in dataframe


def test_metadata_export_passes_filters_as_arrays(simple_project, mocker):
    mocked_api_call = mocker.patch.object(
        simple_project, "_call_api", return_value=(None, None)
    )

    simple_project.export_metadata(
        fields=["field0", "field1", "field2"],
        forms=["form0", "form1", "form2"],
    )

    args, _ = mocked_api_call.call_args

    payload = args[0]

    assert payload["fields[0]"] == "field0"
    assert payload["fields[1]"] == "field1"
    assert payload["fields[2]"] == "field2"
    assert payload["forms[2]"] == "form2"


def test_metadata_export_strictly_enforces_format(simple_project):
    with pytest.raises(ValueError):
        simple_project.export_metadata(format="unsupported")


def test_metadata_import(simple_project):
    data = simple_project.export_metadata()
    response = simple_project.import_metadata(data)

    assert response == len(data)


def test_metadata_csv_import(simple_project):
    metadata_csv_export = simple_project.export_metadata(format="csv")
    response = simple_project.import_metadata(metadata_csv_export, format="csv")

    assert response == 1


def test_metadata_df_import(simple_project):
    dataframe = simple_project.export_metadata(format="df")
    response = simple_project.import_metadata(dataframe)

    assert response == 1


def test_reduced_metadata_import(simple_project):
    original_data = simple_project.export_metadata()
    # reducing the metadata
    reduced_data = original_data[0:1]
    imported_data = simple_project.import_metadata(reduced_data)

    assert len(reduced_data) == imported_data


def test_json_export(simple_project):
    data = simple_project.export_records()

    assert is_json(data)


def test_csv_export(simple_project):
    csv_export = simple_project.export_records(format="csv")
    data = pd.read_csv(StringIO(csv_export))

    assert len(data) == 1


def test_df_export(simple_project):
    dataframe = simple_project.export_records(format="df")

    assert isinstance(dataframe, pd.DataFrame)
    # Test it's a normal index
    assert hasattr(dataframe.index, "name")


def test_export_with_date_filters(simple_project):
    all_records = simple_project.export_records()
    limited_records = simple_project.export_records(
        date_begin=datetime(2021, 11, 1), date_end=datetime(2021, 11, 2)
    )

    assert len(all_records) > len(limited_records)


def test_export_records_strictly_enforces_format(simple_project):
    with pytest.raises(ValueError):
        simple_project.export_records(format="unsupported")


def test_fem_export_passes_filters_as_arrays(simple_project, mocker):
    mocked_api_call = mocker.patch.object(
        simple_project, "_call_api", return_value=(None, None)
    )

    simple_project.export_fem(arms=["arm0", "arm1", "arm2"])

    args, _ = mocked_api_call.call_args

    payload = args[0]

    assert payload["arms[0]"] == "arm0"
    assert payload["arms[1]"] == "arm1"
    assert payload["arms[2]"] == "arm2"


def test_df_export_correctly_uses_df_kwargs(simple_project):
    dataframe = simple_project.export_records(
        format="df", df_kwargs={"index_col": "first_name"}
    )
    assert dataframe.index.name == "first_name"
    # the default index column is just a regular column
    assert "study_id" in dataframe


def test_df_export_handles_eav_type(simple_project):
    data = simple_project.export_records(format="df", type="eav")

    assert isinstance(data, pd.DataFrame)


def test_export_survey_fields_doesnt_include_survey_fields(simple_project):
    """For the simple project there is no survey. But we should still
    be able to call this method anyway.
    """
    records = simple_project.export_records(export_survey_fields=True)
    for record in records:
        assert "redcap_survey_identifier" not in record
        assert "demographics_timestamp" not in record


def test_export_checkbox_labels(simple_project):
    checkbox_label = simple_project.export_records(
        raw_or_label="label", export_checkbox_labels=True
    )[0]["matcheck1___1"]
    assert checkbox_label == "Foo"


def test_export_always_include_def_field(simple_project):
    # If we just ask for a form, must also get def_field in there
    records = simple_project.export_records(forms=["imaging"])
    for record in records:
        assert simple_project.def_field in record
    # still need it def_field even if not asked for in form and fields
    records = simple_project.export_records(forms=["imaging"], fields=["foo_score"])
    for record in records:
        assert simple_project.def_field in record
    # If we just ask for some fields, still need def_field
    records = simple_project.export_records(fields=["foo_score"])
    for record in records:
        assert simple_project.def_field in record
    records = simple_project.export_records(fields=["record_id", "foo_score"])
    for record in records:
        assert simple_project.def_field in record


def test_export_data_access_groups(simple_project):
    records = simple_project.export_records(export_data_access_groups=True)
    for record in records:
        assert "redcap_data_access_group" in record
    # When not passed, that key shouldn't be there
    records = simple_project.export_records()
    for record in records:
        assert not "redcap_data_access_group" in record


def test_export_methods_handle_empty_data_error(simple_project, mocker):
    mocker.patch.object(simple_project, "_call_api", return_value=("\n", {}))

    dataframe = simple_project.export_records(format="df")
    assert dataframe.empty

    dataframe = simple_project.export_fem(format="df")
    assert dataframe.empty

    dataframe = simple_project.export_metadata(format="df")
    assert dataframe.empty


def test_import_records(simple_project):
    data = simple_project.export_records()
    response = simple_project.import_records(data)

    assert "count" in response
    assert not "error" in response


def test_bad_import_throws_exception(simple_project):
    data = simple_project.export_records()
    data[0]["non_existent_key"] = "foo"

    with pytest.raises(RedcapError) as assert_context:
        simple_project.import_records(data)

    assert "error" in repr(assert_context)


def test_df_import(simple_project):
    dataframe = simple_project.export_records(format="df")
    response = simple_project.import_records(dataframe)

    assert "count" in response
    assert not "error" in response


def test_reports_json_export(simple_project):
    report = simple_project.export_reports(report_id="1")

    assert is_json(report)


def test_reports_df_export(simple_project):
    report = simple_project.export_reports(report_id="1", format="df")

    assert isinstance(report, pd.DataFrame)


def test_reports_export_stricly_enforces_format(simple_project):
    with pytest.raises(ValueError):
        simple_project.export_reports(report_id="1", format="unsupported")
