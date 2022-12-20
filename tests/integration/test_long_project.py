"""Test suite for longitudinal REDCap Project against real REDCap server"""
# pylint: disable=missing-function-docstring
import os

import pytest


if not os.getenv("REDCAPDEMO_SUPERUSER_TOKEN"):
    pytest.skip(
        "Super user token not found, skipping integration tests",
        allow_module_level=True,
    )


@pytest.mark.integration
def test_is_longitudinal(long_project):
    assert long_project.is_longitudinal


@pytest.mark.integration
def test_survey_participant_export(long_project):
    data = long_project.export_survey_participant_list(
        instrument="contact_info", event="enrollment_arm_1"
    )
    assert len(data) == 1

    data = long_project.export_survey_participant_list(
        instrument="contact_info", format_type="df", event="enrollment_arm_1"
    )
    assert "email" in data.columns


@pytest.mark.integration
def test_project_info_export(long_project):
    data = long_project.export_project_info()
    assert data["purpose"] == 0


@pytest.mark.integration
def test_users_export(long_project):
    data = long_project.export_users(format_type="df", df_kwargs={"index_col": "email"})
    assert data.index.name == "email"


@pytest.mark.integration
def test_users_import_and_delete(long_project):
    test_user = "pandeharris@gmail.com"
    test_user_json = [{"username": test_user}]
    res = long_project.import_users(test_user_json, return_format_type="csv")

    assert res == "1"

    res = long_project.delete_users([test_user])

    assert res == 1


@pytest.mark.integration
def test_records_export_labeled_headers(long_project):
    data = long_project.export_records(format_type="csv", raw_or_label_headers="label")
    assert "Study ID" in data


@pytest.mark.integration
def test_repeating_export(long_project):
    rep = long_project.export_repeating_instruments_events(format_type="json")

    assert isinstance(rep, list)


@pytest.mark.integration
def test_repeating_export_strictly_enfores_format(long_project):
    with pytest.raises(ValueError):
        long_project.export_repeating_instruments_events(format_type="unsupported")


@pytest.mark.integration
def test_import_export_repeating_forms(long_project):
    for format_type in ["xml", "json", "csv", "df"]:
        rep = long_project.export_repeating_instruments_events(format_type=format_type)
        res = long_project.import_repeating_instruments_events(
            to_import=rep, import_format=format_type
        )
        assert res == 1


@pytest.mark.integration
def test_limit_export_records_forms_and_fields(long_project):
    # only request forms
    records_df = long_project.export_records(
        forms=["demographics", "baseline_data"], format_type="df"
    )
    complete_cols = [col for col in records_df.columns if col.endswith("_complete")]

    assert long_project.def_field in records_df.index.names
    assert complete_cols == ["demographics_complete", "baseline_data_complete"]
    # only request fields
    records_df = long_project.export_records(
        fields=["study_comments"], format_type="df"
    )
    assert long_project.def_field in records_df.index.names
    # request forms and fields
    records_df = long_project.export_records(
        forms=["baseline_data"], fields=["study_comments"], format_type="df"
    )
    complete_cols = [col for col in records_df.columns if col.endswith("_complete")]

    assert long_project.def_field in records_df.index.names
    assert complete_cols == ["baseline_data_complete"]
