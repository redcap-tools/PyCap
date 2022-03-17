"""REDCap API methods for Project metadata"""
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union, overload

from redcap.methods.base import Base, Json

if TYPE_CHECKING:
    import pandas as pd


class Metadata(Base):
    """Responsible for all API methods under 'Metadata' in the API Playground"""

    @overload
    def export_metadata(
        self,
        format_type: Literal["json"],
        fields: Optional[List[str]] = None,
        forms: Optional[List[str]] = None,
        df_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Json:
        ...

    @overload
    def export_metadata(
        self,
        format_type: Literal["csv", "xml"],
        fields: Optional[List[str]] = None,
        forms: Optional[List[str]] = None,
        df_kwargs: Optional[Dict[str, Any]] = None,
    ) -> str:
        ...

    @overload
    def export_metadata(
        self,
        format_type: Literal["df"],
        fields: Optional[List[str]] = None,
        forms: Optional[List[str]] = None,
        df_kwargs: Optional[Dict[str, Any]] = None,
    ) -> "pd.DataFrame":
        ...

    def export_metadata(
        self,
        format_type: Literal["json", "csv", "xml", "df"] = "json",
        fields: Optional[List[str]] = None,
        forms: Optional[List[str]] = None,
        df_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """
        Export the project's metadata

        Args:
            format_type:
                Return the metadata in native objects, csv, or xml.
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
            >>> proj.export_metadata(format_type="df")
                           form_name  section_header  ... matrix_ranking field_annotation
            field_name                                ...
            record_id         form_1             NaN  ...            NaN              NaN
            field_1           form_1             NaN  ...            NaN              NaN
            checkbox_field    form_1             NaN  ...            NaN              NaN
            upload_field      form_1             NaN  ...            NaN              NaN
            ...
        """
        payload = self._initialize_payload(content="metadata", format_type=format_type)
        to_add = [fields, forms]
        str_add = ["fields", "forms"]
        for key, data in zip(str_add, to_add):
            if data:
                for i, value in enumerate(data):
                    payload[f"{key}[{i}]"] = value

        return_type = self._lookup_return_type(format_type, request_type="export")
        response = self._call_api(payload, return_type)

        return self._return_data(
            response=response,
            content="metadata",
            format_type=format_type,
            df_kwargs=df_kwargs,
        )

    @overload
    def import_metadata(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["json"],
        import_format: Literal["json", "csv", "xml", "df"] = "json",
        date_format: Literal["YMD", "DMY", "MDY"] = "YMD",
    ) -> int:
        ...

    @overload
    def import_metadata(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["csv", "xml"],
        import_format: Literal["json", "csv", "xml", "df"] = "json",
        date_format: Literal["YMD", "DMY", "MDY"] = "YMD",
    ) -> str:
        ...

    def import_metadata(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["json", "csv", "xml"] = "json",
        import_format: Literal["json", "csv", "xml", "df"] = "json",
        date_format: Literal["YMD", "DMY", "MDY"] = "YMD",
    ):
        """
        Import metadata (Data Dictionary) into the REDCap Project

        Args:
            to_import: array of dicts, csv/xml string, `pandas.DataFrame`
                Note:
                    If you pass a csv or xml string, you should use the
                    `format` parameter appropriately.
            return_format_type:
                Response format. By default, response will be json-decoded.
            import_format:
                Format of incoming data. By default, to_import will be json-encoded
            date_format:
                Describes the formatting of dates. By default, date strings
                are formatted as 'YYYY-MM-DD' corresponding to 'YMD'. If date
                strings are formatted as 'MM/DD/YYYY' set this parameter as
                'MDY' and if formatted as 'DD/MM/YYYY' set as 'DMY'. No
                other formattings are allowed.

        Returns:
            Union[int, str]: The number of imported fields

        Examples:
            >>> metadata = proj.export_metadata(format_type="csv")
            >>> proj.import_metadata(metadata, import_format="csv")
            4
        """
        payload = self._initialize_import_payload(
            to_import=to_import,
            import_format=import_format,
            return_format_type=return_format_type,
            data_type="metadata",
        )

        # pylint: disable=unsupported-assignment-operation
        payload["dateFormat"] = date_format
        # pylint: enable=unsupported-assignment-operation
        return_type = self._lookup_return_type(
            format_type=return_format_type, request_type="import"
        )
        response = self._call_api(payload, return_type)

        return response
