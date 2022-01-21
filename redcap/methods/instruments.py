"""REDCap API methods for Project instruments"""
from io import StringIO
from typing import TYPE_CHECKING, Any, Dict, List, Optional, overload

from typing_extensions import Literal

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
        df_kwargs: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        ...

    @overload
    def export_instrument_event_mappings(
        self,
        format_type: Literal["csv", "xml"],
        arms: Optional[List[str]] = None,
        df_kwargs: Optional[Dict] = None,
    ) -> str:
        ...

    @overload
    def export_instrument_event_mappings(
        self,
        format_type: Literal["df"],
        arms: Optional[List[str]] = None,
        df_kwargs: Optional[Dict] = None,
    ) -> "pd.DataFrame":
        ...

    def export_instrument_event_mappings(
        self,
        format_type: Literal["json", "csv", "xml", "df"] = "json",
        arms: Optional[List[str]] = None,
        df_kwargs: Optional[Dict] = None,
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

        return_type = self._lookup_return_type(format_type)
        response = self._call_api(payload, return_type)

        if format_type in ("json", "csv", "xml"):
            return response
        if not df_kwargs:
            df_kwargs = {}

        return self._read_csv(StringIO(response), **df_kwargs)
