"""REDCap API methods for Project metadata"""
from io import StringIO

from typing import TYPE_CHECKING, Dict, List, Optional, Union, overload

from typing_extensions import Literal

from redcap.methods.base import Base

if TYPE_CHECKING:
    import pandas as pd


class Metadata(Base):
    """Responsible for all API methods under 'Metadata' in the API Playground"""

    # pylint: disable=redefined-builtin
    @overload
    def export_metadata(
        self,
        format: Literal["json"],
        fields: Optional[List[str]] = None,
        forms: Optional[List[str]] = None,
        df_kwargs: Optional[Dict] = None,
    ) -> List[Dict]:
        ...

    @overload
    def export_metadata(
        self,
        format: Literal["csv", "xml"],
        fields: Optional[List[str]] = None,
        forms: Optional[List[str]] = None,
        df_kwargs: Optional[Dict] = None,
    ) -> str:
        ...

    @overload
    def export_metadata(
        self,
        format: Literal["df"],
        fields: Optional[List[str]] = None,
        forms: Optional[List[str]] = None,
        df_kwargs: Optional[Dict] = None,
    ) -> "pd.DataFrame":
        ...

    def export_metadata(
        self,
        format: Literal["json", "csv", "xml", "df"] = "json",
        fields: Optional[List[str]] = None,
        forms: Optional[List[str]] = None,
        df_kwargs: Optional[Dict] = None,
    ) -> Union[str, List[Dict], "pd.DataFrame"]:
        """
        Export the project's metadata

        Args:
            format:
                Return the metadata in native objects, csv or xml.
                `'df'` will return a `pandas.DataFrame`
            fields: Limit exported metadata to these fields
            forms: Limit exported metadata to these forms
            df_kwargs:
                Passed to `pandas.read_csv` to control construction of
                returned DataFrame.
                By default `{'index_col': 'field_name'}`

        Returns:
            Union[str, List[Dict], pd.DataFrame]: Metadata structure for the project.

        Examples:
            >>> proj.export_metadata(format="df")
                           form_name  section_header  ... matrix_ranking field_annotation
            field_name                                ...
            record_id         form_1             NaN  ...            NaN              NaN
            field_1           form_1             NaN  ...            NaN              NaN
            checkbox_field    form_1             NaN  ...            NaN              NaN
            upload_field      form_1             NaN  ...            NaN              NaN
            ...
        """
        ret_format = format
        if format == "df":
            ret_format = "csv"
        payload = self._basepl("metadata", format=ret_format)
        to_add = [fields, forms]
        str_add = ["fields", "forms"]
        for key, data in zip(str_add, to_add):
            if data:
                for i, value in enumerate(data):
                    payload[f"{key}[{i}]"] = value

        response = self._call_api(payload, "metadata")
        if format in ("json", "csv", "xml"):
            return response
        if format != "df":
            raise ValueError(f"Unsupported format: '{format}'")

        if not df_kwargs:
            df_kwargs = {"index_col": "field_name"}
        return self._read_csv(StringIO(response), **df_kwargs)

    @overload
    def import_metadata(
        self,
        to_import: Union[str, List[Dict], "pd.DataFrame"],
        return_format: Literal["json"],
        format: Literal["json", "csv", "xml", "df"] = "json",
        date_format: Literal["YMD", "DMY", "MDY"] = "YMD",
    ) -> int:
        ...

    @overload
    def import_metadata(
        self,
        to_import: Union[str, List[Dict], "pd.DataFrame"],
        return_format: Literal["csv", "xml"],
        format: Literal["json", "csv", "xml", "df"] = "json",
        date_format: Literal["YMD", "DMY", "MDY"] = "YMD",
    ) -> str:
        ...

    def import_metadata(
        self,
        to_import: Union[str, List[Dict], "pd.DataFrame"],
        return_format: Literal["json", "csv", "xml"] = "json",
        format: Literal["json", "csv", "xml", "df"] = "json",
        date_format: Literal["YMD", "DMY", "MDY"] = "YMD",
    ):
        """
        Import metadata (Data Dictionary) into the REDCap Project

        Args:
            to_import: array of dicts, csv/xml string, `pandas.DataFrame`
                Note:
                    If you pass a csv or xml string, you should use the
                    `format` parameter appropriately.
            return_format:
                Response format. By default, response will be json-decoded.
            format:
                Format of incoming data. By default, to_import will be json-encoded
            date_format:
                Describes the formatting of dates. By default, date strings
                are formatted as 'YYYY-MM-DD' corresponding to 'YMD'. If date
                strings are formatted as 'MM/DD/YYYY' set this parameter as
                'MDY' and if formatted as 'DD/MM/YYYY' set as 'DMY'. No
                other formattings are allowed.

        Returns:
            Union[int, str]: Response from REDCap API, json-decoded if
            `return_format == 'json'`. If successful, the number of imported fields

        Examples:
            >>> metadata = proj.export_metadata(format="csv")
            >>> proj.import_metadata(metadata, format="csv")
            4
        """
        payload = self._initialize_import_payload(to_import, format, "metadata")
        payload["returnFormat"] = return_format
        payload["dateFormat"] = date_format
        response = self._call_api(payload, "imp_metadata")

        return response

    # pylint: enable=redefined-builtin
