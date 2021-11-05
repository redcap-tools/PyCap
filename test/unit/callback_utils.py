"""Utility functions for unit test callbacks"""

import json
from typing import Callable

from urllib import parse

from requests import Request

MockResponse = tuple[int, dict, dict]


def parse_request(req: Request) -> list[dict, str]:
    """Extract the body of a request into a dict"""
    parsed = parse.urlparse(f"?{req.body}")
    data = parse.parse_qs(parsed.query)
    headers = {"Content-Type": "application/json"}

    try:
        request_type = data["content"][0]
    except KeyError as missing_key:
        if " filename" in str(data):
            # file import doesn't have 'content' key
            request_type = "file"
        else:
            raise missing_key

    return [data, headers, request_type]


def handle_arms_request(**kwargs) -> MockResponse:
    """Handle arms export, used at project initialization"""
    headers = kwargs["headers"]
    resp = {"error": "no arms"}

    return (201, headers, json.dumps(resp))


def handle_events_request(**kwargs) -> MockResponse:
    """Handle events export, used at project initialization"""
    headers = kwargs["headers"]
    resp = {"error": "no events"}

    return (201, headers, json.dumps(resp))


def handle_file_request(**kwargs) -> MockResponse:
    """Handle file import/export requests"""
    data = kwargs["data"]
    headers = kwargs["headers"]
    resp = {}
    # file export
    if " filename" not in str(data):
        # name of the data file that was imported
        headers["content-type"] = "text/plain;name=data.txt"

    return (201, headers, json.dumps(resp))


def handle_generate_next_record_name_request(**kwargs) -> MockResponse:
    """Handle generating next record name"""
    headers = kwargs["headers"]
    resp = 123

    return (201, headers, json.dumps(resp))


def handle_metadata_request(**kwargs) -> MockResponse:
    """Handle metadata import/export request"""
    data = kwargs["data"]
    headers = kwargs["headers"]
    # import_metadata
    if "data" in data:
        data_len = len(json.loads(data["data"][0]))
        resp = json.dumps(data_len)
        return (201, headers, resp)
    # exporting metadata
    if "csv" in data["format"]:
        resp = (
            "field_name,field_label,form_name,arm_num,name\n"
            "record_id,Record ID,Test Form,1,test\n"
        )
        headers = {"content-type": "text/csv; charset=utf-8"}
        return (201, headers, resp)

    resp = [
        {
            "field_name": "record_id",
            "field_label": "Record ID",
            "form_name": "Test Form",
            "arm_num": 1,
            "name": "test",
            "field_type": "text",
        },
        {
            "field_name": "file",
            "field_label": "File",
            "form_name": "Test Form",
            "arm_num": 1,
            "name": "file",
            "field_type": "file",
        },
        {
            "field_name": "dob",
            "field_label": "Date of Birth",
            "form_name": "Test Form",
            "arm_num": 1,
            "name": "dob",
            "field_type": "date",
        },
    ]

    return (201, headers, json.dumps(resp))


def handle_project_info_request(**kwargs) -> MockResponse:
    """Handle project info export request"""
    headers = kwargs["headers"]
    resp = {"project_id": 123}

    return (201, headers, json.dumps(resp))


def handle_records_request(**kwargs) -> MockResponse:
    """Handle records import/export request"""
    data = kwargs["data"]
    headers = kwargs["headers"]
    # record import
    if "returnContent" in data:
        if "non_existent_key" in data["data"][0]:
            resp = {"error": "invalid field"}
        else:
            resp = {"count": 1}
    # record export
    elif "csv" in data["format"]:
        resp = "record_id,test,first_name,study_id\n1,1,Peter,1"
        headers = {"content-type": "text/csv; charset=utf-8"}
        # don't want to convert this response to json
        return (201, headers, resp)

    elif "exportDataAccessGroups" in data:
        resp = [
            {
                "field_name": "record_id",
                "redcap_data_access_group": "group1",
            },
            {
                "field_name": "test",
                "redcap_data_access_group": "group1",
            },
        ]
    elif "label" in data.get("rawOrLabel"):
        resp = [{"matcheck1___1": "Foo"}]
    else:
        resp = [
            {"record_id": "1", "test": "test1"},
            {"record_id": "2", "test": "test"},
        ]

    return (201, headers, json.dumps(resp))


def handle_user_request(**kwargs) -> MockResponse:
    """Handle user export"""
    headers = kwargs["headers"]
    resp = [
        {
            "firstname": "test",
            "lastname": "test",
            "email": "test",
            "username": "test",
            "expiration": "test",
            "data_access_group": "test",
            "data_export": "test",
            "forms": "test",
        }
    ]

    return (201, headers, json.dumps(resp))


# pylint: disable=unused-argument
def handle_version_request(**kwargs) -> MockResponse:
    """Handle REDCap version request"""
    resp = b"11.2.3"
    headers = {"content-type": "text/csv; charset=utf-8"}
    return (201, headers, resp)


# pylint: enable=unused-argument


def get_request_handler(request_type: str) -> Callable:
    """Given a request type, extract the handler function"""
    handlers_dict = {
        "arm": handle_arms_request,
        "event": handle_events_request,
        "file": handle_file_request,
        "generateNextRecordName": handle_generate_next_record_name_request,
        "metadata": handle_metadata_request,
        "project": handle_project_info_request,
        "record": handle_records_request,
        "user": handle_user_request,
        "version": handle_version_request,
    }

    return handlers_dict[request_type]
