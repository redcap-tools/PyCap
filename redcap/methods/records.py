"""REDCap API methods for Project records"""
from datetime import datetime

from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union, overload

from redcap.methods.base import Base, EmptyJson, Json

if TYPE_CHECKING:
    import pandas as pd


class Records(Base):
    """Responsible for all API methods under 'Records' in the API Playground"""

    # pylint: disable=too-many-locals
    @overload
    def export_records(
        self,
        format_type: Literal["json"],
        records: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
        forms: Optional[List[str]] = None,
        events: Optional[List[str]] = None,
        raw_or_label: Literal["raw", "label", "both"] = "raw",
        raw_or_label_headers: Literal["raw", "label"] = "raw",
        event_name: Literal["label", "unique"] = "label",
        record_type: Literal["flat", "eav"] = "flat",
        export_survey_fields: bool = False,
        export_data_access_groups: bool = False,
        df_kwargs: Optional[Dict[str, Any]] = None,
        export_checkbox_labels: bool = False,
        filter_logic: Optional[str] = None,
        date_begin: Optional[datetime] = None,
        date_end: Optional[datetime] = None,
    ) -> Json:
        ...

    @overload
    def export_records(
        self,
        format_type: Literal["csv", "xml"],
        records: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
        forms: Optional[List[str]] = None,
        events: Optional[List[str]] = None,
        raw_or_label: Literal["raw", "label", "both"] = "raw",
        raw_or_label_headers: Literal["raw", "label"] = "raw",
        event_name: Literal["label", "unique"] = "label",
        record_type: Literal["flat", "eav"] = "flat",
        export_survey_fields: bool = False,
        export_data_access_groups: bool = False,
        df_kwargs: Optional[Dict[str, Any]] = None,
        export_checkbox_labels: bool = False,
        filter_logic: Optional[str] = None,
        date_begin: Optional[datetime] = None,
        date_end: Optional[datetime] = None,
    ) -> str:
        ...

    @overload
    def export_records(
        self,
        format_type: Literal["df"],
        records: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
        forms: Optional[List[str]] = None,
        events: Optional[List[str]] = None,
        raw_or_label: Literal["raw", "label", "both"] = "raw",
        raw_or_label_headers: Literal["raw", "label"] = "raw",
        event_name: Literal["label", "unique"] = "label",
        record_type: Literal["flat", "eav"] = "flat",
        export_survey_fields: bool = False,
        export_data_access_groups: bool = False,
        df_kwargs: Optional[Dict[str, Any]] = None,
        export_checkbox_labels: bool = False,
        filter_logic: Optional[str] = None,
        date_begin: Optional[datetime] = None,
        date_end: Optional[datetime] = None,
    ) -> "pd.DataFrame":
        ...

    def export_records(
        self,
        format_type: Literal["json", "csv", "xml", "df"] = "json",
        records: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
        forms: Optional[List[str]] = None,
        events: Optional[List[str]] = None,
        raw_or_label: Literal["raw", "label", "both"] = "raw",
        raw_or_label_headers: Literal["raw", "label"] = "raw",
        event_name: Literal["label", "unique"] = "label",
        record_type: Literal["flat", "eav"] = "flat",
        export_survey_fields: bool = False,
        export_data_access_groups: bool = False,
        df_kwargs: Optional[Dict[str, Any]] = None,
        export_checkbox_labels: bool = False,
        filter_logic: Optional[str] = None,
        date_begin: Optional[datetime] = None,
        date_end: Optional[datetime] = None,
    ):
        # pylint: disable=line-too-long
        """
        Export data from the REDCap project.

        Args:
            format_type:
                Format of returned data. `'json'` returns json-decoded
                objects while `'csv'` and `'xml'` return other formats.
                `'df'` will attempt to return a `pandas.DataFrame`
            records:
                Array of record names specifying specific records to export.
                By default, all records are exported
            fields:
                Array of field names specifying specific fields to pull
                by default, all fields are exported
            forms:
                Array of form names to export. If in the web UI, the form
                name has a space in it, replace the space with an underscore
                By default, all forms are exported
            events:
                An array of unique event names from which to export records
                Note:
                    This only applies to longitudinal projects
            raw_or_label:
                Export the raw coded values or labels for the options of
                multiple choice fields, or both
            raw_or_label_headers:
                Export the column names of the instrument as their raw
                value or their labeled value
            event_name:
                Export the unique event name or the event label
            record_type:
                Database output structure type
            export_survey_fields:
                Specifies whether or not to export the survey identifier
                field (e.g., "redcap_survey_identifier") or survey timestamp
                fields (e.g., form_name+"_timestamp") when surveys are
                utilized in the project
            export_data_access_groups:
                Specifies whether or not to export the
                `"redcap_data_access_group"` field when data access groups
                are utilized in the project

                Note:
                    This flag is only viable if the user whose token is
                    being used to make the API request is *not* in a data
                    access group. If the user is in a group, then this flag
                    will revert to its default value.
            df_kwargs:
                Passed to `pandas.read_csv` to control construction of
                returned DataFrame.
                By default, `{'index_col': self.def_field}`
            export_checkbox_labels:
                Specify whether to export checkbox values as their label on
                export.
            filter_logic:
                Filter which records are returned using REDCap conditional syntax
            date_begin:
                Filter on records created after a date
            date_end:
                Filter on records created before a date

        Returns:
            Union[List[Dict[str, Any]], str, pd.DataFrame]: Exported data

        Examples:
            >>> proj.export_records()
            [{'record_id': '1', 'redcap_event_name': 'event_1_arm_1', 'field_1': '1',
            'checkbox_field___1': '0', 'checkbox_field___2': '1', 'upload_field': 'test_upload.txt',
            'form_1_complete': '2'},
            {'record_id': '2', 'redcap_event_name': 'event_1_arm_1', 'field_1': '0',
            'checkbox_field___1': '0', 'checkbox_field___2': '0', 'upload_field': 'myupload.txt',
            'form_1_complete': '0'}]

            >>> proj.export_records(filter_logic="[field_1] = 1")
            [{'record_id': '1', 'redcap_event_name': 'event_1_arm_1', 'field_1': '1',
            'checkbox_field___1': '0', 'checkbox_field___2': '1', 'upload_field': 'test_upload.txt',
            'form_1_complete': '2'}]

            >>> proj.export_records(
            ...     format_type="csv",
            ...     fields=["field_1", "checkbox_field"],
            ...     raw_or_label="label"
            ... )
            'field_1,checkbox_field___1,checkbox_field___2\\nYes,Unchecked,Checked\\nNo,Unchecked,Unchecked\\n'

            >>> import pandas as pd
            >>> pd.set_option("display.max_columns", 3)
            >>> proj.export_records(format_type="df")
                                         field_1  ...  form_1_complete
            record_id redcap_event_name           ...
            1         event_1_arm_1            1  ...                2
            2         event_1_arm_1            0  ...                0
            ...
        """
        # pylint: enable=line-too-long
        payload = self._initialize_payload(
            content="record", format_type=format_type, record_type=record_type
        )
        keys_to_add = (
            records,
            fields,
            forms,
            events,
            raw_or_label,
            raw_or_label_headers,
            event_name,
            export_survey_fields,
            export_data_access_groups,
            export_checkbox_labels,
        )

        str_keys = (
            "records",
            "fields",
            "forms",
            "events",
            "rawOrLabel",
            "rawOrLabelHeaders",
            "eventName",
            "exportSurveyFields",
            "exportDataAccessGroups",
            "exportCheckboxLabel",
        )

        for key, data in zip(str_keys, keys_to_add):
            if data:
                if key in ("fields", "records", "forms", "events"):
                    for i, value in enumerate(data):
                        payload[f"{ key }[{ i }]"] = value
                else:
                    payload[key] = data

        if date_begin:
            payload["dateRangeBegin"] = date_begin.strftime("%Y-%m-%d %H:%M:%S")

        if date_end:
            payload["dateRangeEnd"] = date_end.strftime("%Y-%m-%d %H:%M:%S")

        if filter_logic:
            payload["filterLogic"] = filter_logic

        return_type = self._lookup_return_type(format_type, request_type="export")
        response = self._call_api(payload, return_type)

        return self._return_data(
            response=response,
            content="record",
            format_type=format_type,
            df_kwargs=df_kwargs,
            record_type=record_type,
        )

    # pylint: enable=too-many-locals

    @overload
    def import_records(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["json"],
        return_content: Literal["count", "auto_ids"],
        overwrite: Literal["normal", "overwrite"] = "normal",
        import_format: Literal["json", "csv", "xml", "df"] = "json",
        date_format: Literal["YMD", "DMY", "MDY"] = "YMD",
        force_auto_number: bool = False,
    ) -> Dict[str, int]:
        ...

    @overload
    def import_records(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["json"],
        return_content: Literal["ids"],
        overwrite: Literal["normal", "overwrite"] = "normal",
        import_format: Literal["json", "csv", "xml", "df"] = "json",
        date_format: Literal["YMD", "DMY", "MDY"] = "YMD",
        force_auto_number: bool = False,
    ) -> List[str]:
        ...

    @overload
    def import_records(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["json"],
        return_content: Literal["nothing"],
        overwrite: Literal["normal", "overwrite"] = "normal",
        import_format: Literal["json", "csv", "xml", "df"] = "json",
        date_format: Literal["YMD", "DMY", "MDY"] = "YMD",
        force_auto_number: bool = False,
    ) -> EmptyJson:
        ...

    @overload
    def import_records(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["csv", "xml"],
        return_content: Literal["count", "ids", "auto_ids", "nothing"],
        overwrite: Literal["normal", "overwrite"] = "normal",
        import_format: Literal["json", "csv", "xml", "df"] = "json",
        date_format: Literal["YMD", "DMY", "MDY"] = "YMD",
        force_auto_number: bool = False,
    ) -> str:
        ...

    def import_records(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["json", "csv", "xml"] = "json",
        return_content: Literal["count", "ids", "auto_ids", "nothing"] = "count",
        overwrite: Literal["normal", "overwrite"] = "normal",
        import_format: Literal["json", "csv", "xml", "df"] = "json",
        date_format: Literal["YMD", "DMY", "MDY"] = "YMD",
        force_auto_number: bool = False,
    ):
        """
        Import data into the RedCap Project

        Args:
            to_import:
                Note:
                    If you pass a df, csv, or xml string, you should use the
                    `format` parameter appropriately.
                Note:
                    Keys of the dictionaries should be subset of project's,
                    fields, but this isn't a requirement. If you provide keys
                    that aren't defined fields, the returned response will
                    contain an `'error'` key.
            return_format_type:
                Response format. By default, response will be json-decoded.
            return_content:
                By default, the response contains a 'count' key with the number of
                records just imported. By specifying 'ids', a list of ids
                imported will be returned. 'nothing' will only return
                the HTTP status code and no message.
            overwrite:
                `'overwrite'` will erase values previously stored in the
                database if not specified in the to_import dictionaries.
            import_format:
                Format of incoming data. By default, to_import will be json-encoded
            date_format:
                Describes the formatting of dates. By default, date strings
                are formatted as 'YYYY-MM-DD' corresponding to 'YMD'. If date
                strings are formatted as 'MM/DD/YYYY' set this parameter as
                'MDY' and if formatted as 'DD/MM/YYYY' set as 'DMY'. No
                other formattings are allowed.
            force_auto_number:
                Enables automatic assignment of record IDs
                of imported records by REDCap. If this is set to true, and auto-numbering
                for records is enabled for the project, auto-numbering of imported records
                will be enabled.

        Raises:
            RedcapError: Bad request made, double check field names and other inputs

        Returns:
            Union[Dict, str]: response from REDCap API, json-decoded if `return_format` == `'json'`

        Examples:
            >>> new_record = [{"record_id": 3, "field_1": 1}]
            >>> proj.import_records(new_record)
            {'count': 1}
        """
        payload = self._initialize_import_payload(
            to_import=to_import,
            import_format=import_format,
            return_format_type=return_format_type,
            data_type="record",
        )

        # pylint: disable=unsupported-assignment-operation
        payload["overwriteBehavior"] = overwrite
        payload["returnContent"] = return_content
        payload["dateFormat"] = date_format
        payload["forceAutoNumber"] = force_auto_number
        # pylint: enable=unsupported-assignment-operation

        return_type = self._lookup_return_type(
            format_type=return_format_type,
            request_type="import",
            import_records_format=return_content,
        )
        response = self._call_api(payload, return_type)

        return response

    @overload
    def delete_records(
        self, records: List[str], return_format_type: Literal["json"]
    ) -> int:
        ...

    @overload
    def delete_records(
        self, records: List[str], return_format_type: Literal["csv", "xml"]
    ) -> str:
        ...

    def delete_records(
        self,
        records: List[str],
        return_format_type: Literal["json", "csv", "xml"] = "json",
    ):
        """
        Delete records from the project.

        Args:
            records: List of record IDs to delete from the project

        Returns:
            Union[int, str]: Number of records deleted

        Examples:
            >>> new_record = [{"record_id": 3, "field_1": 1}, {"record_id": 4}]
            >>> proj.import_records(new_record)
            {'count': 2}
            >>> proj.delete_records(["3", "4"])
            2
        """
        payload = self._initialize_payload(
            content="record", return_format_type=return_format_type
        )
        payload["action"] = "delete"
        # Turn list of records into dict, and append to payload
        records_dict = {
            f"records[{ idx }]": record for idx, record in enumerate(records)
        }
        payload.update(records_dict)

        return_type = self._lookup_return_type(
            format_type=return_format_type, request_type="delete"
        )
        response = self._call_api(payload, return_type)
        return response

    def generate_next_record_name(self) -> str:
        """
        Get the next record name

        Returns:
            The next record name for a project with auto-numbering records enabled

        Examples:
            >>> proj.generate_next_record_name()
            '3'
        """
        # Force the csv format here since if the project uses data access groups
        # or just non-standard record names then the result will not be JSON-compliant
        payload = self._initialize_payload(
            content="generateNextRecordName", format_type="csv"
        )

        return self._call_api(payload, return_type="str")
