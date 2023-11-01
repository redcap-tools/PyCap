"""Utility functions for unit test callbacks"""

import json

from typing import Any, Callable, List, Union

from urllib import parse


def is_json(data: List[dict]):
    """Shorthand assertion for a json data structure"""
    is_list = isinstance(data, list)

    is_list_of_dicts = True
    for record in data:
        if not isinstance(record, dict):
            is_list_of_dicts = False
            break

    return is_list and is_list_of_dicts


def parse_request(req: Any) -> List[Union[dict, str]]:
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


def handle_simple_project_arms_request(**kwargs) -> Any:
    """Handle Arm requests for simple project"""
    headers = kwargs["headers"]
    resp = {"error": "You cannot export arms for classic projects"}

    return (400, headers, json.dumps(resp))


def handle_long_project_arms_request(**kwargs) -> Any:
    """Handle Arm requests for long project"""
    headers = kwargs["headers"]
    data = kwargs["data"]
    # Arm import (JSON only)
    if "data" in str(data):
        override = json.loads(data["override"][0])
        if override == 0:
            resp = 1
        elif override == 1:
            resp = 2
        else:
            resp = {"error": "test error"}
    # Arm delete (JSON only)
    elif "delete" in str(data):
        resp = 1
    # Arm export (JSON only)
    else:
        # Check for optional arms arg
        arms = data.get("arms[0]", [])
        if len(arms):
            resp = [{"arm_num": 2, "name": "test_2"}]
        else:
            resp = [{"arm_num": 1, "name": "test_1"}]

    return (201, headers, json.dumps(resp))


def handle_simple_project_events_request(**kwargs) -> Any:
    """Handle Event requests for simple project"""
    headers = kwargs["headers"]
    resp = {"error": "You cannot export events for classic projects"}

    return (400, headers, json.dumps(resp))


def handle_long_project_events_request(**kwargs) -> Any:
    """Handle Event requests for long project"""
    headers = kwargs["headers"]
    data = kwargs["data"]
    # Event import (JSON only)
    if "data" in str(data):
        override = json.loads(data["override"][0])
        if override == 0:
            resp = 1
        elif override == 1:
            resp = 2
        else:
            resp = {"error": "test error"}
    # Event delete (JSON only)
    elif "delete" in str(data):
        resp = 1
    # Event export (JSON only)
    else:
        # Check for optional arms arg
        arms = data.get("arms[0]", [])
        if len(arms):
            resp = [
                {
                    "event_name": "Event 1",
                    "arm_num": 1,
                    "unique_event_name": "event_1_arm_1",
                    "custom_event_label": "",
                    "event_id": 1,
                },
                {
                    "event_name": "Event 2",
                    "arm_num": 1,
                    "unique_event_name": "event_2_arm_1",
                    "custom_event_label": "",
                    "event_id": 2,
                },
            ]

        else:
            resp = [
                {
                    "event_name": "Event 1",
                    "arm_num": 1,
                    "unique_event_name": "event_1_arm_1",
                    "custom_event_label": "",
                    "event_id": 1,
                }
            ]

    return (201, headers, json.dumps(resp))


def handle_dag_request(**kwargs) -> Any:
    """Handle DAG requests"""
    headers = kwargs["headers"]
    data = kwargs["data"]
    # DAG import (JSON only)
    if "data" in str(data):
        resp = json.dumps(1)
    # DAG delete (JSON only)
    elif "delete" in str(data):
        resp = json.dumps(1)
    # DAG delete (csv only)
    elif "switch" in str(data):
        resp = "1"
    # DAG export (JSON only)
    else:
        resp = [
            {"data_access_group_name": "New DAG", "unique_group_name": "new_dag"},
            {"data_access_group_name": "Test DAG", "unique_group_name": "test_dag"},
        ]
        resp = json.dumps(resp)

    return (201, headers, resp)


def handle_user_dag_assignment_request(**kwargs):
    """Handle User-DAG assignment requests"""
    headers = kwargs["headers"]
    data = kwargs["data"]
    # User-DAG import (JSON only)
    if "data" in str(data):
        resp = 1
    # User-DAG export (JSON only)
    else:
        resp = [
            {"username": "user1@gmail.com", "redcap_data_access_group": "test_dag"},
            {"username": "user2@gmail.com", "redcap_data_access_group": ""},
        ]

    return (201, headers, json.dumps(resp))


def handle_export_field_names_request(**kwargs) -> Any:
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


def handle_simple_project_form_event_mapping_request(**kwargs) -> Any:
    """Handle events export, used at project initialization"""
    headers = kwargs["headers"]
    resp = {"error": "You cannot export form/event mappings for classic projects"}

    return (400, headers, json.dumps(resp))


def handle_simple_project_instruments_request(**kwargs) -> Any:
    """Handle Instrument requests for simple project"""
    headers = kwargs["headers"]

    # Instrument export (JSON only)
    resp = [{"instrument_name": "form_1", "instrument_label": "Form 1"}]

    return (201, headers, json.dumps(resp))


def handle_simple_project_pdf_request(**kwargs) -> Any:
    """Handle PDF requests for simple project"""
    headers = kwargs["headers"]
    resp = {}

    return (201, headers, json.dumps(resp))


def handle_long_project_instruments_request(**kwargs) -> Any:
    """Handle Instrument requests for long project"""
    headers = kwargs["headers"]

    # Instrument export (JSON only)
    resp = [
        {"instrument_name": "form_1", "instrument_label": "Form 1"},
        {"instrument_name": "form_2", "instrument_label": "Form 2"},
        {"instrument_name": "form_3", "instrument_label": "Form 3"},
    ]

    return (201, headers, json.dumps(resp))


def handle_long_project_pdf_request(**kwargs) -> Any:
    """Handle PDF requests for long project"""
    headers = kwargs["headers"]
    resp = {}

    return (201, headers, json.dumps(resp))


def handle_long_project_form_event_mapping_request(**kwargs) -> Any:
    """Handle instrument-event mappings for long project"""
    headers = kwargs["headers"]
    data = kwargs["data"]
    # FEM import (JSON only)
    if "data" in str(data):
        resp = 1
    # FEM export (JSON only)
    else:
        resp = [{"arm_num": 1, "unique_event_name": "raw", "form": "form_1"}]

    return (201, headers, json.dumps(resp))


def handle_long_project_repeating_form_request(**kwargs) -> Any:
    """Give back list of repeating instruments for long project"""
    headers = kwargs["headers"]
    data = kwargs["data"]
    resp = None
    # import (JSON only)
    if "data" in data:
        repeat_forms = json.loads(data["data"][0])
        resp = len(repeat_forms)
    # export (JSON only)
    else:
        resp = [{"form_name": "testform", "custom_form_label": ""}]

    return (201, headers, json.dumps(resp))


def handle_simple_project_file_request(**kwargs) -> Any:
    """Handle file import/export requests"""
    data = kwargs["data"]
    headers = kwargs["headers"]
    resp = {}
    # file export
    if " filename" not in str(data):
        # name of the data file that was imported
        headers["content-type"] = "text/plain;name=data.txt"

    return (201, headers, json.dumps(resp))


def handle_long_project_file_request(**kwargs) -> Any:
    """Handle file import/export/delete requests"""
    # test using blank headers
    data = kwargs["data"]
    headers = kwargs["headers"]
    resp = {}
    # file export
    if " filename" not in str(data):
        # name of the data file that was imported
        headers["content-type"] = "text/plain;name=data.txt"

    return (201, headers, json.dumps(resp))


def handle_generate_next_record_name_request(**kwargs) -> Any:
    """Handle generating next record name"""
    headers = kwargs["headers"]
    resp = 123

    return (201, headers, json.dumps(resp))


def handle_logging_request(**kwargs) -> Any:
    """Handle logging request"""
    headers = kwargs["headers"]
    data = kwargs["data"]
    # export (JSON only)
    if "beginTime" in data:
        resp = [
            {
                "timestamp": "2022-03-30 10:50",
                "username": "myuser",
                "action": "Manage/Design",
                "details": "Add/edit branching logic",
            },
            {
                "timestamp": "2022-03-29 10:49",
                "username": "myuser",
                "action": "Manage/Design ",
                "details": "Delete project field",
            },
        ]
    else:
        resp = [
            {
                "timestamp": "2022-03-30 10:50",
                "username": "myuser",
                "action": "Manage/Design",
                "details": "Add/edit branching logic",
            },
            {
                "timestamp": "2022-03-29 10:49",
                "username": "myuser",
                "action": "Manage/Design ",
                "details": "Delete project field",
            },
            {
                "timestamp": "2022-03-28 10:49",
                "username": "myuser",
                "action": "Manage/Design ",
                "details": "Delete project field",
            },
        ]

    return (201, headers, json.dumps(resp))


def handle_simple_project_metadata_request(**kwargs) -> Any:
    """Handle metadata import/export request"""
    data = kwargs["data"]
    headers = kwargs["headers"]
    # import_metadata
    if "data" in data:
        if "csv" in data["format"]:
            # count newlines to infer number of records
            newline_count = str(data["data"][0].count("\n") - 1)
            data_len = json.loads(str.encode(newline_count))
        else:
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


def handle_long_project_metadata_request(**kwargs) -> Any:
    """Handle metadata export for long project"""
    data = kwargs["data"]
    headers = kwargs["headers"]
    # import metadata
    if "data" in data:
        resp = {"error": "test error"}
    else:
        resp = [
            {
                "field_name": "record_id",
                "field_label": "Record ID",
                "form_name": "Test Form",
                "field_type": "text",
                "arm_num": 1,
                "name": "test",
            },
            {
                "field_name": "file",
                "field_label": "test",
                "form_name": "Test Form",
                "field_type": "file",
                "arm_num": 1,
                "name": "file",
            },
        ]

    return (201, headers, json.dumps(resp))


def handle_project_info_request(**kwargs) -> Any:
    """Handle project info export request"""
    headers = kwargs["headers"]
    resp = {"project_id": 123}

    return (201, headers, json.dumps(resp))


def handle_simple_project_delete_records(data: dict) -> int:
    """Given simple project delete request, determine how many records were deleted"""
    resp = 0
    for key in data:
        if "records[" in key:
            resp += 1

    if data["returnFormat"] in ["csv", "xml"]:
        resp = str(resp)

    return resp


def handle_simple_project_import_records(data: dict) -> dict:
    """Given simple project import request, determine response"""
    resp = {"count": 2}

    if "non_existent_key" in data["data"][0]:
        resp = {"error": "invalid field"}

    return_content = data["returnContent"][0]
    if return_content == "ids":
        resp = ["1", "2"]
    elif return_content == "nothing":
        resp = {}

    return resp


def handle_simple_project_records_request(**kwargs) -> Any:
    """Handle records import/export request"""
    data = kwargs["data"]
    headers = kwargs["headers"]
    status_code = 201
    if "delete" in data.get("action", "other"):
        resp = handle_simple_project_delete_records(data)
    elif "returnContent" in data:
        resp = handle_simple_project_import_records(data)
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
    elif "label" in data.get("rawOrLabel", "raw"):
        resp = [{"matcheck1___1": "Foo"}]
    elif data.get("dateRangeBegin") and data.get("dateRangeEnd"):
        resp = [{"record_id": "1", "test": "test1"}]
    # mock a malformed request errors
    elif "bad_request" in str(data):
        status_code = 400
        resp = {"error": "this is a bad request"}
    else:
        resp = [
            {"record_id": "1", "test": "test1"},
            {"record_id": "2", "test": "test"},
        ]

    return (status_code, headers, json.dumps(resp))


def handle_long_project_records_request(**kwargs) -> Any:
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


def handle_survey_project_records_request(**kwargs) -> Any:
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


def handle_simple_project_reports_request(**kwargs) -> Any:
    """Export report data from project"""
    data = kwargs["data"]
    headers = kwargs["headers"]
    resp = None
    # We must receive a report id in order to give a response
    if "1" in data.get("report_id"):
        if "csv" in data["format"]:
            resp = "record_id,date_col,test_col_1,test_col_2\n1,2015-04-08,test,1"
            headers = {"content-type": "text/csv; charset=utf-8"}
            return (201, headers, resp)

        resp = [
            {
                "record_id": "1",
                "date_col": "2015-04-08",
                "test_col_1": "test",
                "test_col_2": "1",
            },
            {
                "neo_data_request_id": "2",
                "date_col": "2015-04-01",
                "test_col_1": "test",
                "test_col_2": "",
            },
        ]

    return (201, headers, json.dumps(resp))


def handle_long_project_reports_request(**kwargs) -> Any:
    """Export report data from long project, csv only for now"""
    data = kwargs["data"]
    headers = kwargs["headers"]
    resp = None
    # We must receive a report id in order to give a response
    if "1" in data.get("report_id") and "csv" in data["format"]:
        resp = "record_id,redcap_event_name,test_col_1,test_col_2\n1,raw,test,1"
        headers = {"content-type": "text/csv; charset=utf-8"}

    return (201, headers, resp)


def handle_user_request(**kwargs) -> Any:
    """Handle user requests"""
    headers = kwargs["headers"]
    data = kwargs["data"]
    # user import (JSON only)
    if "data" in str(data):
        resp = json.dumps(1)
    # user delete (csv only)
    elif "delete" in str(data):
        resp = "1"
    # user export (JSON only)
    else:
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
        resp = json.dumps(resp)

    return (201, headers, resp)


def handle_user_role_request(**kwargs) -> Any:
    """Handle user role requests"""
    headers = kwargs["headers"]
    data = kwargs["data"]
    # user import (JSON only)
    if "data" in str(data):
        resp = 1
    # user delete (csv only)
    elif "delete" in str(data):
        resp = 1
    # user export (JSON only)
    else:
        resp = [
            {
                "unique_role_name": "Role Name",
                "role_label": "Test role",
                "design": "0",
                "user_rights": "0",
                "data_access_groups": "0",
                "data_export": "0",
                "reports": "0",
                "stats_and_charts": "0",
            }
        ]

    return (201, headers, json.dumps(resp))


def handle_user_role_assignment_request(**kwargs) -> Any:
    """Handle user role mapping requests"""
    headers = kwargs["headers"]
    data = kwargs["data"]
    # user import (JSON only)
    if "data" in str(data):
        resp = 1
    # user export (JSON only)
    else:
        resp = [{"username": "test user", "unique_role_name": "Role Name"}]

    return (201, headers, json.dumps(resp))


# pylint: disable=unused-argument
def handle_simple_project_version_request(**kwargs) -> Any:
    """Handle REDCap version request"""
    resp = b"11.2.3"
    headers = {"content-type": "text/csv; charset=utf-8"}
    return (201, headers, resp)


def handle_long_project_version_request(**kwargs) -> Any:
    """Return error for REDCap version request"""
    resp = b"error"
    headers = {"content-type": "text/csv; charset=utf-8"}
    return (201, headers, resp)


# pylint: enable=unused-argument


def handle_long_project_survey_participants_request(**kwargs) -> Any:
    """Get the survey participants for an instrument"""
    data = kwargs["data"]
    headers = kwargs["headers"]
    resp = None

    if "test" in data.get("instrument") and "raw" in data.get("event"):
        resp = [
            {
                "email": "test1@gmail.com",
                "email_occurrence": 1,
                "identifier": "",
                "record": "",
                "invitation_sent_status": 0,
                "invitation_send_time": "",
                "response_status": 2,
                "survey_access_code": "",
                "survey_link": "",
            },
            {
                "email": "test2@gmail.com",
                "email_occurrence": 1,
                "identifier": "",
                "record": "",
                "invitation_sent_status": 0,
                "invitation_send_time": "",
                "response_status": 2,
                "survey_access_code": "",
                "survey_link": "",
            },
        ]

    return (201, headers, json.dumps(resp))


def get_simple_project_request_handler(request_type: str) -> Callable:
    """Given a request type, extract the handler function"""
    handlers_dict = {
        "arm": handle_simple_project_arms_request,
        "dag": handle_dag_request,
        "event": handle_simple_project_events_request,
        "exportFieldNames": handle_export_field_names_request,
        "file": handle_simple_project_file_request,
        "formEventMapping": handle_simple_project_form_event_mapping_request,
        "generateNextRecordName": handle_generate_next_record_name_request,
        "instrument": handle_simple_project_instruments_request,
        "log": handle_logging_request,
        "metadata": handle_simple_project_metadata_request,
        "pdf": handle_simple_project_pdf_request,
        "project": handle_project_info_request,
        "record": handle_simple_project_records_request,
        "report": handle_simple_project_reports_request,
        "user": handle_user_request,
        "userDagMapping": handle_user_dag_assignment_request,
        "userRole": handle_user_role_request,
        "userRoleMapping": handle_user_role_assignment_request,
        "version": handle_simple_project_version_request,
    }

    return handlers_dict[request_type]


def get_long_project_request_handler(request_type: str) -> Callable:
    """Given a request type, extract the handler function"""
    handlers_dict = {
        "arm": handle_long_project_arms_request,
        "event": handle_long_project_events_request,
        "file": handle_long_project_file_request,
        "formEventMapping": handle_long_project_form_event_mapping_request,
        "instrument": handle_long_project_instruments_request,
        "repeatingFormsEvents": handle_long_project_repeating_form_request,
        "metadata": handle_long_project_metadata_request,
        "participantList": handle_long_project_survey_participants_request,
        "pdf": handle_long_project_pdf_request,
        "record": handle_long_project_records_request,
        "report": handle_long_project_reports_request,
        "version": handle_long_project_version_request,
    }

    return handlers_dict[request_type]


def get_survey_project_request_handler(request_type: str) -> Callable:
    """Given a request type, extract the handler function"""
    handlers_dict = {
        "formEventMapping": handle_simple_project_form_event_mapping_request,
        "metadata": handle_simple_project_metadata_request,
        "record": handle_survey_project_records_request,
    }

    return handlers_dict[request_type]
