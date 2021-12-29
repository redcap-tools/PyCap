"""REDCap API methods for Project records"""
from datetime import datetime
from io import StringIO
from typing import TYPE_CHECKING, Dict, List, Optional, Union, overload

from typing_extensions import Literal

from redcap.request import RedcapError
from redcap.methods.base import Base

if TYPE_CHECKING:
    import pandas as pd


class Records(Base):
    """Responsible for all API methods under 'Records' in the API Playground"""

    # pylint: disable=redefined-builtin
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-locals
    @overload
    def export_records(
        self,
        format: Literal["json"],
        records: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
        forms: Optional[List[str]] = None,
        events: Optional[List[str]] = None,
        raw_or_label: Literal["raw", "label", "both"] = "raw",
        event_name: Literal["label", "unique"] = "label",
        type: Literal["flat", "eav"] = "flat",
        export_survey_fields: bool = False,
        export_data_access_groups: bool = False,
        df_kwargs: Optional[Dict] = None,
        export_checkbox_labels: bool = False,
        filter_logic: Optional[str] = None,
        date_begin: Optional[datetime] = None,
        date_end: Optional[datetime] = None,
    ) -> List[Dict]:
        ...

    @overload
    def export_records(
        self,
        format: Literal["csv", "xml"],
        records: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
        forms: Optional[List[str]] = None,
        events: Optional[List[str]] = None,
        raw_or_label: Literal["raw", "label", "both"] = "raw",
        event_name: Literal["label", "unique"] = "label",
        type: Literal["flat", "eav"] = "flat",
        export_survey_fields: bool = False,
        export_data_access_groups: bool = False,
        df_kwargs: Optional[Dict] = None,
        export_checkbox_labels: bool = False,
        filter_logic: Optional[str] = None,
        date_begin: Optional[datetime] = None,
        date_end: Optional[datetime] = None,
    ) -> str:
        ...

    @overload
    def export_records(
        self,
        format: Literal["df"],
        records: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
        forms: Optional[List[str]] = None,
        events: Optional[List[str]] = None,
        raw_or_label: Literal["raw", "label", "both"] = "raw",
        event_name: Literal["label", "unique"] = "label",
        type: Literal["flat", "eav"] = "flat",
        export_survey_fields: bool = False,
        export_data_access_groups: bool = False,
        df_kwargs: Optional[Dict] = None,
        export_checkbox_labels: bool = False,
        filter_logic: Optional[str] = None,
        date_begin: Optional[datetime] = None,
        date_end: Optional[datetime] = None,
    ) -> "pd.DataFrame":
        ...

    def export_records(
        self,
        format: Literal["json", "csv", "xml", "df"] = "json",
        records: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
        forms: Optional[List[str]] = None,
        events: Optional[List[str]] = None,
        raw_or_label: Literal["raw", "label", "both"] = "raw",
        event_name: Literal["label", "unique"] = "label",
        type: Literal["flat", "eav"] = "flat",
        export_survey_fields: bool = False,
        export_data_access_groups: bool = False,
        df_kwargs: Optional[Dict] = None,
        export_checkbox_labels: bool = False,
        filter_logic: Optional[str] = None,
        date_begin: Optional[datetime] = None,
        date_end: Optional[datetime] = None,
    ):
        """
        Export data from the REDCap project.

        Args:
            format:
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
            event_name:
                Export the unique event name or the event label
            type:
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
            Union[List[Dict], str, pd.DataFrame]: Exported data
        """
        ret_format = format
        if format == "df":
            ret_format = "csv"
        payload = self._basepl("record", format=ret_format, rec_type=type)
        keys_to_add = (
            records,
            fields,
            forms,
            events,
            raw_or_label,
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
        response, _ = self._call_api(payload, "exp_record")
        if format in ("json", "csv", "xml"):
            return response
        if format != "df":
            raise ValueError(f"Unsupported format: '{ format }'")

        if not df_kwargs:
            if type == "eav":
                df_kwargs = {}
            else:
                if self.is_longitudinal:
                    df_kwargs = {"index_col": [self.def_field, "redcap_event_name"]}
                else:
                    df_kwargs = {"index_col": self.def_field}
        buf = StringIO(response)
        dataframe = self._read_csv(buf, **df_kwargs)
        buf.close()

        return dataframe

    # pylint: enable=too-many-branches
    # pylint: enable=too-many-locals

    @overload
    def import_records(
        self,
        to_import: Union[str, List[Dict], "pd.DataFrame"],
        return_format: Literal["json"],
        overwrite: Literal["normal", "overwrite"] = "normal",
        format: Literal["json", "csv", "xml", "df"] = "json",
        return_content: Literal["count", "ids", "nothing"] = "count",
        date_format: Literal["YMD", "DMY", "MDY"] = "YMD",
        force_auto_number: bool = False,
    ) -> Dict:
        ...

    @overload
    def import_records(
        self,
        to_import: Union[str, List[Dict], "pd.DataFrame"],
        return_format: Literal["csv", "xml"],
        overwrite: Literal["normal", "overwrite"] = "normal",
        format: Literal["json", "csv", "xml", "df"] = "json",
        return_content: Literal["count", "ids", "nothing"] = "count",
        date_format: Literal["YMD", "DMY", "MDY"] = "YMD",
        force_auto_number: bool = False,
    ) -> str:
        ...

    def import_records(
        self,
        to_import: Union[str, List[Dict], "pd.DataFrame"],
        return_format: Literal["json", "csv", "xml"] = "json",
        overwrite: Literal["normal", "overwrite"] = "normal",
        format: Literal["json", "csv", "xml", "df"] = "json",
        return_content: Literal["count", "ids", "nothing"] = "count",
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
            return_format:
                Response format. By default, response will be json-decoded.
            overwrite:
                `'overwrite'` will erase values previously stored in the
                database if not specified in the to_import dictionaries.
            format:
                Format of incoming data. By default, to_import will be json-encoded
            return_content:
                By default, the response contains a 'count' key with the number of
                records just imported. By specifying 'ids', a list of ids
                imported will be returned. 'nothing' will only return
                the HTTP status code and no message.
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
            RedcapError: Bad request made, double check field names and inputs

        Returns:
            Union[Dict, str]: response from REDCap API, json-decoded if `return_format` == `'json'`
        """
        payload = self._initialize_import_payload(to_import, format, "record")

        payload["overwriteBehavior"] = overwrite
        payload["returnFormat"] = return_format
        payload["returnContent"] = return_content
        payload["dateFormat"] = date_format
        payload["forceAutoNumber"] = force_auto_number
        response = self._call_api(payload, "imp_record")[0]
        if "error" in response:
            raise RedcapError(str(response))
        return response

    def delete_records(self, records: List[str]) -> int:
        """
        Delete records from the project.

        Args:
            records: List of record IDs to delete from the project

        Returns:
            Number of records deleted
        """
        payload = {}
        payload["action"] = "delete"
        payload["content"] = "record"
        payload["token"] = self.token
        # Turn list of records into dict, and append to payload
        records_dict = {
            f"records[{ idx }]": record for idx, record in enumerate(records)
        }
        payload.update(records_dict)

        payload["format"] = format
        response, _ = self._call_api(payload, "del_record")
        return response

        # pylint: disable=redefined-builtin

    def generate_next_record_name(self) -> str:
        """
        Get the next record name

        Returns:
            The next record name for a project with auto-numbering records enabled
        """
        payload = self._basepl(content="generateNextRecordName")

        return self._call_api(payload, "exp_next_id")[0]
