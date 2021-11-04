#! /usr/bin/env python
"""Test suite for Project class against mocked REDCap server"""
# pylint: disable=missing-function-docstring
from io import StringIO

import pandas as pd
import pytest
import semantic_version

from redcap import Project, RedcapError


def test_bad_creds(project_urls, project_token):
    # this url is "bad" because we didn't set up an response fixture for it
    bad_url = project_urls["bad_url"]

    with pytest.raises(RedcapError):
        Project(bad_url, project_token)
    with pytest.raises(RedcapError):
        Project(bad_url, "1")


def test_init(simple_project):
    assert isinstance(simple_project, Project)


def test_get_version(simple_project):
    assert simple_project.redcap_version == semantic_version.Version("11.2.3")


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


def test_metadata_import(simple_project):
    data = simple_project.export_metadata()
    response = simple_project.import_metadata(data)

    assert response == len(data)


def test_reduced_metadata_import(simple_project):
    original_data = simple_project.export_metadata()
    # reducing the metadata
    reduced_data = original_data[0:1]
    imported_data = simple_project.import_metadata(reduced_data)

    assert len(reduced_data) == imported_data


def test_json_export(simple_project):
    data = simple_project.export_records()

    assert isinstance(data, list)

    for record in data:
        assert isinstance(record, dict)


def test_csv_export(simple_project):
    csv_export = simple_project.export_records(format="csv")
    data = pd.read_csv(StringIO(csv_export))

    assert len(data) == 1


def test_df_export(simple_project):
    dataframe = simple_project.export_records(format="df")

    assert isinstance(dataframe, pd.DataFrame)
    # Test it's a normal index
    assert hasattr(dataframe.index, "name")


def test_df_export_correctly_uses_df_kwargs(simple_project):
    dataframe = simple_project.export_records(
        format="df", df_kwargs={"index_col": "first_name"}
    )
    assert dataframe.index.name == "first_name"
    # the default index column is just a regular column
    assert "study_id" in dataframe


def test_export_methods_handle_empty_data_error(simple_project, mocker):
    mocker.patch.object(simple_project, "_call_api", return_value=("\n", {}))

    dataframe = simple_project.export_records(format="df")
    assert dataframe.empty

    dataframe = simple_project.export_fem(format="df")
    assert dataframe.empty

    dataframe = simple_project.export_metadata(format="df")
    assert dataframe.empty


def test_df_import(simple_project):
    dataframe = simple_project.export_records(format="df")
    response = simple_project.import_records(dataframe)

    assert "count" in response
    assert not "error" in response


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
