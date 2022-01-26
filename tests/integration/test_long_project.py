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


def test_survey_participant_export(long_project):
    data = long_project.export_survey_participant_list(
        instrument="contact_info", event="enrollment_arm_1"
    )
    assert len(data) == 1

    data = long_project.export_survey_participant_list(
        instrument="contact_info", format_type="df", event="enrollment_arm_1"
    )
    assert "email" in data.columns


def test_project_info_export(long_project):
    data = long_project.export_project_info()
    assert data["purpose"] == 0


def test_users_export(long_project):
    data = long_project.export_users(format_type="df", df_kwargs={"index_col": "email"})
    assert data.index.name == "email"


def test_records_export_labeled_headers(long_project):
    data = long_project.export_records(format_type="csv", raw_or_label_headers="label")
    assert "Study ID" in data
