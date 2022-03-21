"""REDCap API methods for Project reports"""
from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, overload

from redcap.methods.base import Base, Json

if TYPE_CHECKING:
    import pandas as pd


class Reports(Base):
    """Responsible for all API methods under 'Reports' in the API Playground"""

    @overload
    def export_report(
        self,
        report_id: str,
        format_type: Literal["json"],
        raw_or_label: Literal["raw", "label"] = "raw",
        raw_or_label_headers: Literal["raw", "label"] = "raw",
        export_checkbox_labels: bool = False,
        csv_delimiter: Literal[",", "tab", ";", "|", "^"] = ",",
        df_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Json:
        ...

    @overload
    def export_report(
        self,
        report_id: str,
        format_type: Literal["csv", "xml"],
        raw_or_label: Literal["raw", "label"] = "raw",
        raw_or_label_headers: Literal["raw", "label"] = "raw",
        export_checkbox_labels: bool = False,
        csv_delimiter: Literal[",", "tab", ";", "|", "^"] = ",",
        df_kwargs: Optional[Dict[str, Any]] = None,
    ) -> str:
        ...

    @overload
    def export_report(
        self,
        report_id: str,
        format_type: Literal["df"],
        raw_or_label: Literal["raw", "label"] = "raw",
        raw_or_label_headers: Literal["raw", "label"] = "raw",
        export_checkbox_labels: bool = False,
        csv_delimiter: Literal[",", "tab", ";", "|", "^"] = ",",
        df_kwargs: Optional[Dict[str, Any]] = None,
    ) -> "pd.DataFrame":
        ...

    def export_report(
        self,
        report_id: str,
        format_type: Literal["json", "csv", "xml", "df"] = "json",
        raw_or_label: Literal["raw", "label"] = "raw",
        raw_or_label_headers: Literal["raw", "label"] = "raw",
        export_checkbox_labels: bool = False,
        csv_delimiter: Literal[",", "tab", ";", "|", "^"] = ",",
        df_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """
        Export a report of the Project

        Args:
            report_id:
                The report ID number provided next to the report name
                on the report list page
            format_type:
                Format of returned data. `'json'` returns json-decoded
                objects while `'csv'` and `'xml'` return strings.
                `'df'` will attempt to return a `pandas.DataFrame`.
            raw_or_label:
                Export the raw coded values or
                labels for the options of multiple choice fields
            raw_or_label_headers:
                For the CSV headers, export the variable/field names
                (raw) or the field labels (label)
            export_checkbox_labels:
                Specifies the format of
                checkbox field values specifically when exporting the data as labels
                (i.e. when `rawOrLabel=label`). When exporting labels, by default
                (without providing the exportCheckboxLabel flag or if
                exportCheckboxLabel=false), all checkboxes will either have a value
                'Checked' if they are checked or 'Unchecked' if not checked.
                But if exportCheckboxLabel is set to true, it will instead export
                the checkbox value as the checkbox option's label (e.g., 'Choice 1')
                if checked or it will be blank/empty (no value) if not checked
            csv_delimiter:
                For the csv format, choose how the csv delimiter.

        Raises:
            ValueError: Unsupported format specified

        Returns:
            Union[List[Dict[str, Any]], str, pd.DataFrame]: Data from the report ordered by
            the record (primary key of project) and then by event id

        Examples:
            >>> proj.export_report(report_id="4292") # doctest: +SKIP
            [{'record_id': '1', 'redcap_event_name': 'event_1_arm_1',
            'checkbox_field___1': '0', 'checkbox_field___2': '1'}]
        """
        payload = self._initialize_payload(content="report", format_type=format_type)
        keys_to_add = (
            report_id,
            raw_or_label,
            raw_or_label_headers,
            export_checkbox_labels,
            csv_delimiter,
        )
        str_keys = (
            "report_id",
            "rawOrLabel",
            "rawOrLabelHeaders",
            "exportCheckboxLabel",
            "csvDelimiter",
        )
        for key, data in zip(str_keys, keys_to_add):
            if data:
                payload[key] = data

        return_type = self._lookup_return_type(format_type, request_type="export")
        response = self._call_api(payload, return_type)

        return self._return_data(
            response=response,
            content="report",
            format_type=format_type,
            df_kwargs=df_kwargs,
        )
