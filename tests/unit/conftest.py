"""Test fixtures for unit tests only"""
from typing import Dict

import pytest
import responses


@pytest.fixture(scope="module")
def project_token() -> str:
    """Project API token"""
    return "0" * 32


@pytest.fixture(scope="module")
def project_urls() -> Dict[str, str]:
    """Different urls for different mock projects"""
    return {
        "bad_url": "https://redcap.badproject.edu/api",
        "long_project": "https://redcap.longproject.edu/api/",
        "simple_project": "https://redcap.simpleproject.edu/api/",
        "survey_project": "https://redcap.surveyproject.edu/api/",
    }


# See here for docs: https://github.com/getsentry/responses#responses-as-a-pytest-fixture
@pytest.fixture(scope="module")
def mocked_responses() -> responses.RequestsMock:
    """Base fixture for all mocked responses"""
    with responses.RequestsMock() as resps:
        yield resps
