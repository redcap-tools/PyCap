"""Test suite for Project class against real REDCap server"""
# pylint: disable=missing-function-docstring
import os

import pytest


if not os.getenv("REDCAPDEMO_SUPERUSER_TOKEN"):
    pytest.skip(
        "Super user token not found, skipping integration tests",
        allow_module_level=True,
    )


def test_export_of_simple_project(simple_project):
    proj_records_export = simple_project.export_records()
    assert len(proj_records_export) == 3


def test_import_of_simple_project(simple_project):
    test_records = [{"record_id": i} for i in range(4, 7)]
    res = simple_project.import_records(test_records)
    assert res["count"] == len(test_records)
