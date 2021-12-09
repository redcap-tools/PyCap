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
    assert long_project.is_longitudinal()
