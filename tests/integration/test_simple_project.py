"""Test suite for simple REDCap Project against real REDCap server"""
# pylint: disable=missing-function-docstring
import os

import pytest


if not os.getenv("REDCAPDEMO_SUPERUSER_TOKEN"):
    pytest.skip(
        "Super user token not found, skipping integration tests",
        allow_module_level=True,
    )


@pytest.mark.integration
def test_is_not_longitudinal(simple_project):
    assert not simple_project.is_longitudinal()


@pytest.mark.integration
def test_export_records(simple_project):
    proj_records_export = simple_project.export_records()
    assert len(proj_records_export) == 3


@pytest.mark.integration
def test_export_records_df(simple_project):
    proj_records_export = simple_project.export_records(format="df")
    assert len(proj_records_export) == 3


@pytest.mark.integration
def test_export_records_df_eav(simple_project):
    proj_records_export = simple_project.export_records(format="df", type="eav")
    assert len(proj_records_export) == 31


@pytest.mark.integration
def test_import_and_delete_records(simple_project):
    new_record_ids = [4, 5, 6]
    test_records = [{"record_id": i} for i in new_record_ids]

    res = simple_project.import_records(test_records)
    assert res["count"] == len(test_records)

    res = simple_project.delete_records(new_record_ids)
    assert res == "3"
