"""REDCap API methods for Project reports"""
from io import StringIO
from typing import TYPE_CHECKING, Dict, List, Optional, overload

from typing_extensions import Literal

from redcap.methods.base import Base

if TYPE_CHECKING:
    import pandas as pd


class Reports(Base):
    """Responsible for all API methods under 'Reports' in the API Playground"""

    # pylint: disable=redefined-builtin
    # pylint: disable=too-many-locals
    @overload
    def export_report(
        self,
        report_id: str,
        format: Literal["json"],
        raw_or_label: Literal["raw", "label"] = "raw",
        raw_or_label_headers: Literal["raw", "label"] = "raw",
        export_checkbox_labels: bool = False,
        csv_delimiter: Literal[",", "tab", ";", "|", "^"] = ",",
        df_kwargs: Optional[Dict] = None,
    ) -> List[Dict]:
        ...

    @overload
    def export_report(
        self,
        report_id: str,
        format: Literal["csv", "xml"],
        raw_or_label: Literal["raw", "label"] = "raw",
        raw_or_label_headers: Literal["raw", "label"] = "raw",
        export_checkbox_labels: bool = False,
        csv_delimiter: Literal[",", "tab", ";", "|", "^"] = ",",
        df_kwargs: Optional[Dict] = None,
    ) -> str:
        ...

    @overload
    def export_report(
        self,
        report_id: str,
        format: Literal["df"],
        raw_or_label: Literal["raw", "label"] = "raw",
        raw_or_label_headers: Literal["raw", "label"] = "raw",
        export_checkbox_labels: bool = False,
        csv_delimiter: Literal[",", "tab", ";", "|", "^"] = ",",
        df_kwargs: Optional[Dict] = None,
    ) -> "pd.DataFrame":
        ...

    def export_report(
        self,
        report_id: str,
        format: Literal["json", "csv", "xml", "df"] = "json",
        raw_or_label: Literal["raw", "label"] = "raw",
        raw_or_label_headers: Literal["raw", "label"] = "raw",
        export_checkbox_labels: bool = False,
        csv_delimiter: Literal[",", "tab", ";", "|", "^"] = ",",
        df_kwargs: Optional[Dict] = None,
    ):
        """
        Export a report of the Project

        Args:
            report_id:
                The report ID number provided next to the report name
                on the report list page
            format:
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
            Union[List[Dict], str, pd.DataFrame]: Data from the report ordered by
            the record (primary key of project) and then by event id
        """

        ret_format = format
        if format == "df":
            ret_format = "csv"

        payload = self._basepl(content="report", format=ret_format)
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
        response, _ = self._call_api(payload, "exp_report")
        if format in ("json", "csv", "xml"):
            return response
        if format != "df":
            raise ValueError(f"Unsupported format: '{ format }'")

        if not df_kwargs:
            if self.is_longitudinal:
                df_kwargs = {"index_col": [self.def_field, "redcap_event_name"]}
            else:
                df_kwargs = {"index_col": self.def_field}
        buf = StringIO(response)
        dataframe = self._read_csv(buf, **df_kwargs)
        buf.close()

        return dataframe

    # pylint: enable=too-many-locals
    # pylint: enable=redefined-builtin
