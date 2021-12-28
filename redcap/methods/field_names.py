"""REDCap API methods for Project field names"""
from io import StringIO
from typing import TYPE_CHECKING, Dict, List, Optional, overload, Union

from redcap.methods.base import Base

if TYPE_CHECKING:
    import pandas as pd


class FieldNames(Base):
    """Responsible for all API methods under 'Field Names' in the API Playground"""

    # pylint: disable=redefined-builtin
    @overload
    def export_field_names(
        self, field: str, format: str = "json", df_kwargs: Optional[Dict] = None
    ) -> str:
        ...

    @overload
    def export_field_names(
        self, field: None = None, format: str = "json", df_kwargs: Optional[Dict] = None
    ) -> Union[List[Dict], "pd.DataFrame"]:
        ...

    def export_field_names(
        self,
        field: Optional[str] = None,
        format: str = "json",
        df_kwargs: Optional[Dict] = None,
    ):
        """
        Export the project's export field names

        Args:
            field:
                Limit exported field name to this field (only single field supported).
                When not provided, all fields returned
            format: `'json'`, `'csv'`, `'xml'`, `'df'`
                Return the metadata in native objects, csv or xml.
                `'df'` will return a `pandas.DataFrame`
            df_kwargs:
                Passed to `pandas.read_csv` to control construction of
                returned DataFrame.
                by default `{'index_col': 'original_field_name'}`

        Returns:
            Union[str, List[Dict], "pd.DataFrame"]: Metadata structure for the project.
        """
        ret_format = format
        if format == "df":
            ret_format = "csv"

        payload = self._basepl("exportFieldNames", format=ret_format)

        if field:
            payload["field"] = field

        response, _ = self._call_api(payload, "exp_field_names")
        if format in ("json", "csv", "xml"):
            return response
        if format != "df":
            raise ValueError(f"Unsupported format: '{format}'")
        if not df_kwargs:
            df_kwargs = {"index_col": "original_field_name"}
        return self._read_csv(StringIO(response), **df_kwargs)

    # pylint: enable=redefined-builtin
