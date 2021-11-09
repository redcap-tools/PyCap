"""Utility functions for unit test callbacks"""

import json
from typing import Callable, List, Tuple, Union

from urllib import parse

from requests import Request

MockResponse = Tuple[int, dict, dict]


def parse_request(req: Request) -> List[Union[dict, str]]:
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


def handle_simple_project_arms_request(**kwargs) -> MockResponse:
    """Handle arms export, used at project initialization"""
    headers = kwargs["headers"]
    resp = {"error": "no arms"}

    return (201, headers, json.dumps(resp))


def handle_long_project_arms_request(**kwargs) -> MockResponse:
    """Give back list of arms for long project"""
    headers = kwargs["headers"]
    resp = [{"arm_num": 1, "name": "test"}]

    return (201, headers, json.dumps(resp))


def handle_simple_project_events_request(**kwargs) -> MockResponse:
    """Handle events export, used at project initialization"""
    headers = kwargs["headers"]
    resp = {"error": "no events"}

    return (201, headers, json.dumps(resp))


def handle_long_project_events_request(**kwargs) -> MockResponse:
    """Give back list of events for long project"""
    headers = kwargs["headers"]
    resp = [{"unique_event_name": "raw"}]

    return (201, headers, json.dumps(resp))


def handle_export_field_names_request(**kwargs) -> MockResponse:
    """Give back list of project export field names"""
    data = kwargs["data"]
    headers = kwargs["headers"]
    resp = [
        {
            "original_field_name": "record_id",
            "choice_value": "",
            "export_field_name": "record_id",
        },
        {
            "original_field_name": "test",
            "choice_value": "1",
            "export_field_name": "test___1",
        },
    ]

    if "csv" in str(data):
        headers = {"content-type": "text/csv; charset=utf-8"}
        resp = (
            "original_field_name,choice_value,export_field_name\n",
            "record_id,,record_id\ntest,1,test___1",
        )

        if "field" in str(data):
            resp = "original_field_name,choice_value,export_field_name\ntest,1,test___1"

        return (201, headers, resp)

    return (201, headers, json.dumps(resp))


def handle_form_event_mapping_request(**kwargs) -> MockResponse:
    """Handle form event mapping export for long project"""
    headers = kwargs["headers"]
    resp = [{"field_name": "record_id"}, {"field_name": "test"}]

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


def handle_simple_project_metadata_request(**kwargs) -> MockResponse:
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


def handle_long_project_metadata_request(**kwargs) -> MockResponse:
    """Handle metadata export for long project"""
    headers = kwargs["headers"]
    resp = [
        {
            "field_name": "record_id",
            "field_label": "Record ID",
            "form_name": "Test Form",
            "arm_num": 1,
            "name": "test",
        }
    ]

    return (201, headers, json.dumps(resp))


def handle_project_info_request(**kwargs) -> MockResponse:
    """Handle project info export request"""
    headers = kwargs["headers"]
    resp = {"project_id": 123}

    return (201, headers, json.dumps(resp))


def handle_simple_project_records_request(**kwargs) -> MockResponse:
    """Handle records import/export request"""
    data = kwargs["data"]
    headers = kwargs["headers"]
    status_code = 201
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
        return (status_code, headers, resp)

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
    elif data.get("dateRangeBegin") and data.get("dateRangeEnd"):
        resp = [{"record_id": "1", "test": "test1"}]
    # mock a malformed request errors
    elif "bad_request" in str(data):
        status_code = 400
        resp = {}
    elif "server_error" in str(data):
        status_code = 500
        resp = {}
    else:
        resp = [
            {"record_id": "1", "test": "test1"},
            {"record_id": "2", "test": "test"},
        ]

    return (status_code, headers, json.dumps(resp))


def handle_long_project_records_request(**kwargs) -> MockResponse:
    """Handle csv export for long project"""
    data = kwargs["data"]
    # if the None value gets returned it means the test failed
    resp = None
    headers = kwargs["headers"]
    # data import
    if "returnContent" in data:
        resp = {"count": 1}

        return (201, headers, json.dumps(resp))
    if "csv" in data["format"]:
        resp = "record_id,test,redcap_event_name\n1,1,raw"
        headers = {"content-type": "text/csv; charset=utf-8"}
    elif "raw" in data["events[0]"]:
        resp = json.dumps(
            [
                {"record_id": "1", "test": "test1"},
                {"record_id": "2", "test": "test"},
            ]
        )

    return (201, headers, resp)


def handle_survey_project_records_request(**kwargs) -> MockResponse:
    """Handle export with survey fields requested"""
    headers = kwargs["headers"]
    data = kwargs["data"]
    # if the None value gets returned it means the test failed
    resp = None
    if data["exportSurveyFields"]:
        resp = [
            {
                "field_name": "record_id",
                "redcap_survey_identifier": "test",
                "demographics_timestamp": "a_real_date",
            },
            {
                "field_name": "test",
                "redcap_survey_identifier": "test",
                "demographics_timestamp": "a_real_date",
            },
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
def handle_simple_project_version_request(**kwargs) -> MockResponse:
    """Handle REDCap version request"""
    resp = b"11.2.3"
    headers = {"content-type": "text/csv; charset=utf-8"}
    return (201, headers, resp)


def handle_long_project_version_request(**kwargs) -> MockResponse:
    """Handle REDCap version request, where version is unavailable"""
    resp = {"error": "no version found"}
    headers = {"content-type": "text/csv; charset=utf-8"}
    return (201, headers, json.dumps(resp))


# pylint: enable=unused-argument


def get_simple_project_request_handler(request_type: str) -> Callable:
    """Given a request type, extract the handler function"""
    handlers_dict = {
        "arm": handle_simple_project_arms_request,
        "event": handle_simple_project_events_request,
        "exportFieldNames": handle_export_field_names_request,
        "file": handle_file_request,
        "generateNextRecordName": handle_generate_next_record_name_request,
        "metadata": handle_simple_project_metadata_request,
        "project": handle_project_info_request,
        "record": handle_simple_project_records_request,
        "user": handle_user_request,
        "version": handle_simple_project_version_request,
    }

    return handlers_dict[request_type]


def get_long_project_request_handler(request_type: str) -> Callable:
    """Given a request type, extract the handler function"""
    handlers_dict = {
        "arm": handle_long_project_arms_request,
        "event": handle_long_project_events_request,
        "formEventMapping": handle_form_event_mapping_request,
        "metadata": handle_long_project_metadata_request,
        "record": handle_long_project_records_request,
        "version": handle_long_project_version_request,
    }

    return handlers_dict[request_type]


def get_survey_project_request_handler(request_type: str) -> Callable:
    """Given a request type, extract the handler function"""
    handlers_dict = {
        "arm": handle_simple_project_arms_request,
        "event": handle_simple_project_events_request,
        "metadata": handle_simple_project_metadata_request,
        "record": handle_survey_project_records_request,
        "version": handle_simple_project_version_request,
    }

    return handlers_dict[request_type]
