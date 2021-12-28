"""REDCap API methods for Project instruments"""
from io import StringIO
from typing import TYPE_CHECKING, Dict, List, Optional, overload

from typing_extensions import Literal

from redcap.methods.base import Base

if TYPE_CHECKING:
    import pandas as pd


class Instruments(Base):
    """Responsible for all API methods under 'Instruments' in the API Playground"""

    # pylint: disable=redefined-builtin
    @overload
    def export_instrument_event_mappings(
        self,
        format: Literal["json"],
        arms: Optional[List[str]] = None,
        df_kwargs: Optional[Dict] = None,
    ) -> List[Dict]:
        ...

    @overload
    def export_instrument_event_mappings(
        self,
        format: Literal["csv", "xml"],
        arms: Optional[List[str]] = None,
        df_kwargs: Optional[Dict] = None,
    ) -> str:
        ...

    @overload
    def export_instrument_event_mappings(
        self,
        format: Literal["df"],
        arms: Optional[List[str]] = None,
        df_kwargs: Optional[Dict] = None,
    ) -> "pd.DataFrame":
        ...

    def export_instrument_event_mappings(
        self,
        format: Literal["json", "csv", "xml", "df"] = "json",
        arms: Optional[List[str]] = None,
        df_kwargs: Optional[Dict] = None,
    ):
        """
        Export the project's instrument to event mapping

        Args:
            format:
                Return the form event mappings in native objects,
                csv or xml, `'df''` will return a `pandas.DataFrame`
            arms: Limit exported form event mappings to these arm numbers
            df_kwargs:
                Passed to pandas.read_csv to control construction of
                returned DataFrame

        Returns:
            Union[str, List[Dict], pd.DataFrame]: Instrument-event mapping for the project
        """
        ret_format = format
        if format == "df":
            ret_format = "csv"
        payload = self._basepl("formEventMapping", format=ret_format)

        if arms:
            for i, value in enumerate(arms):
                payload[f"arms[{ i }]"] = value

        response, _ = self._call_api(payload, "exp_fem")
        if format in ("json", "csv", "xml"):
            return response
        if format != "df":
            raise ValueError(f"Unsupported format: '{ format }'")
        if not df_kwargs:
            df_kwargs = {}

        return self._read_csv(StringIO(response), **df_kwargs)

    # pylint: enable=redefined-builtin
