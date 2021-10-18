"""Test suite for Project class against real REDCap server"""
# pylint: disable=missing-function-docstring
import os

import pytest
from redcap import Project


@pytest.mark.skipif(
    True, reason="Need to migrate to GitHub Actions before testing on CI"
)
def test_export_of_simple_project():
    url = "https://redcapdemo.vanderbilt.edu/api/"
    token = os.getenv("REDCAPDEMO_SIMPLE_TOKEN")
    simple_proj = Project(url, token)
    proj_records_export = simple_proj.export_records()
    assert len(proj_records_export) == 3
