"""REDCap API methods for Project instruments"""
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, overload

from redcap.methods.base import Base

if TYPE_CHECKING:
    import pandas as pd


class Instruments(Base):
    """Responsible for all API methods under 'Instruments' in the API Playground"""

    @overload
    def export_instrument_event_mappings(
        self,
        format_type: Literal["json"],
        arms: Optional[List[str]] = None,
        df_kwargs: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        ...

    @overload
    def export_instrument_event_mappings(
        self,
        format_type: Literal["csv", "xml"],
        arms: Optional[List[str]] = None,
        df_kwargs: Optional[Dict[str, Any]] = None,
    ) -> str:
        ...

    @overload
    def export_instrument_event_mappings(
        self,
        format_type: Literal["df"],
        arms: Optional[List[str]] = None,
        df_kwargs: Optional[Dict[str, Any]] = None,
    ) -> "pd.DataFrame":
        ...

    def export_instrument_event_mappings(
        self,
        format_type: Literal["json", "csv", "xml", "df"] = "json",
        arms: Optional[List[str]] = None,
        df_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """
        Export the project's instrument to event mapping

        Args:
            format_type:
                Return the form event mappings in native objects,
                csv or xml, `'df''` will return a `pandas.DataFrame`
            arms: Limit exported form event mappings to these arms
            df_kwargs:
                Passed to pandas.read_csv to control construction of
                returned DataFrame

        Returns:
            Union[str, List[Dict[str, Any]], pd.DataFrame]: Instrument-event mapping for the project

        Examples:
            >>> proj.export_instrument_event_mappings()
            [{'arm_num': 1, 'unique_event_name': 'event_1_arm_1', 'form': 'form_1'}]
        """
        payload = self._initialize_payload(
            content="formEventMapping", format_type=format_type
        )

        if arms:
            for i, value in enumerate(arms):
                payload[f"arms[{ i }]"] = value

        return_type = self._lookup_return_type(format_type, request_type="export")
        response = self._call_api(payload, return_type)

        return self._return_data(
            response=response,
            content="formEventMapping",
            format_type=format_type,
            df_kwargs=df_kwargs,
        )
