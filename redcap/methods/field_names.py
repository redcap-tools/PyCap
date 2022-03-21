"""REDCap API methods for Project field names"""
from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, overload

from redcap.methods.base import Base, Json

if TYPE_CHECKING:
    import pandas as pd


class FieldNames(Base):
    """Responsible for all API methods under 'Field Names' in the API Playground"""

    @overload
    def export_field_names(
        self,
        format_type: Literal["json"],
        field: Optional[str],
        df_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Json:
        ...

    @overload
    def export_field_names(
        self,
        format_type: Literal["csv", "xml"],
        field: Optional[str],
        df_kwargs: Optional[Dict[str, Any]] = None,
    ) -> str:
        ...

    @overload
    def export_field_names(
        self,
        format_type: Literal["df"],
        field: Optional[str],
        df_kwargs: Optional[Dict[str, Any]] = None,
    ) -> "pd.DataFrame":
        ...

    def export_field_names(
        self,
        format_type: Literal["json", "csv", "xml", "df"] = "json",
        field: Optional[str] = None,
        df_kwargs: Optional[Dict[str, Any]] = None,
    ):
        # pylint: disable=line-too-long
        """
        Export the project's export field names

        Args:
            format_type:
                Return the metadata in native objects, csv or xml.
                `'df'` will return a `pandas.DataFrame`
            field:
                Limit exported field name to this field (only single field supported).
                When not provided, all fields returned
            df_kwargs:
                Passed to `pandas.read_csv` to control construction of
                returned DataFrame.
                by default `{'index_col': 'original_field_name'}`

        Returns:
            Union[str, List[Dict[str, Any]], "pd.DataFrame"]: Metadata structure for the project.

        Examples:
            >>> proj.export_field_names()
            [{'original_field_name': 'record_id', 'choice_value': '', 'export_field_name': 'record_id'},
            {'original_field_name': 'field_1', 'choice_value': '', 'export_field_name': 'field_1'},
            {'original_field_name': 'checkbox_field', 'choice_value': '1', 'export_field_name': 'checkbox_field___1'},
            {'original_field_name': 'checkbox_field', 'choice_value': '2', 'export_field_name': 'checkbox_field___2'},
            {'original_field_name': 'form_1_complete', 'choice_value': '', 'export_field_name': 'form_1_complete'}]
        """
        # pylint: enable=line-too-long
        payload = self._initialize_payload(
            content="exportFieldNames", format_type=format_type
        )

        if field:
            payload["field"] = field

        return_type = self._lookup_return_type(format_type, request_type="export")
        response = self._call_api(payload, return_type)

        return self._return_data(
            response=response,
            content="exportFieldNames",
            format_type=format_type,
            df_kwargs=df_kwargs,
        )
