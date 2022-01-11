#! /usr/bin/env python
"""Test suite for RCRequest class"""
# pylint: disable=missing-function-docstring
import pytest
import responses

from redcap import RCAPIError, RCRequest


def test_rcrequest_checks_paylods():
    url = "http://httpbin.org"
    payload = {
        "token": "8E66DB6844D58E990075AFB51658A002",
        "format": "json",
        "type": "flat",
    }
    args = [url, payload, "metadata"]
    #  no 'content' key
    with pytest.raises(RCAPIError):
        RCRequest(*args)

    #  wrong content
    payload["content"] = "blahblah"
    with pytest.raises(RCAPIError):
        RCRequest(*args)
    #  good content
    payload["content"] = "metadata"
    res = RCRequest(*args)
    assert isinstance(res, RCRequest)


@responses.activate
def test_newlines_are_handled():
    """Test that newlines are appropriately dealt with"""

    responses.add(responses.POST, "https://redcap.vanderbilt.edu/api/")
    bad_metadata = {
        "token": "B82CB05641E3BE8247E5F852EAFC5C21",
        "format": "json",
        "type": "flat",
        "content": "metadata",
    }

    args = ["https://redcap.vanderbilt.edu/api/", bad_metadata, "metadata"]
    res = RCRequest(*args).execute(verify_ssl=True, file=None)

    assert res is not None
    assert len(res) > 0


def test_survey_participant_list_checks_content():
    payload = {
        "token": "foobar",
        "content": "participantList",
        "format": "json",
        "instrument": "bar",
    }
    url = "https://foobarbat.com"
    req_type = "exp_survey_participant_list"
    # This should not raise
    res = RCRequest(url, payload, req_type)
    assert res is not None

    # This should raise because of a different content
    payload["content"] = "foobar"
    with pytest.raises(RCAPIError):
        RCRequest(url, payload, req_type)
