"""REDCap API methods for Project instruments"""
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union, cast

from redcap.methods.base import Base
from redcap.request import Json

if TYPE_CHECKING:
    import pandas as pd


class Instruments(Base):
    """Responsible for all API methods under 'Instruments' in the API Playground"""

    def export_instruments(
        self,
        format_type: Literal["json", "csv", "xml", "df"] = "json",
    ):
        """
        Export the Instruments of the Project

        Args:
            format_type:
                Response return format

        Returns:
            Union[List[Dict[str, Any]], str, pandas.DataFrame]: List of Instruments

        Examples:
            >>> proj.export_instruments()
            [{'instrument_name': 'demo', 'instrument_label': 'Demographics'}]
        """
        payload = self._initialize_payload(
            content="instrument", format_type=format_type
        )
        return_type = self._lookup_return_type(format_type, request_type="export")
        response = cast(Union[Json, str], self._call_api(payload, return_type))

        return self._return_data(
            response=response,
            content="instrument",
            format_type=format_type,
        )

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
        response = cast(Union[Json, str], self._call_api(payload, return_type))

        return self._return_data(
            response=response,
            content="formEventMapping",
            format_type=format_type,
            df_kwargs=df_kwargs,
        )

    def import_instrument_event_mappings(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["json", "csv", "xml"] = "json",
        import_format: Literal["json", "csv", "xml", "df"] = "json",
    ):
        # pylint: disable=line-too-long
        """
        Import the project's instrument to event mapping

        Note:
            This only works for longitudinal projects.

        Args:
            to_import: array of dicts, csv/xml string, `pandas.DataFrame`
                Note:
                    If you pass a csv or xml string, you should use the
                    `import format` parameter appropriately.
            return_format_type:
                Response format. By default, response will be json-decoded.
            import_format:
                Format of incoming data. By default, import_format
                will be json-encoded

        Returns:
            Union[int, str]: Number of instrument-event mappings imported

        Examples:
            Import instrument-event mappings
            >>> instrument_event_mappings = [{"arm_num": "1", "unique_event_name": "event_1_arm_1", "form": "form_1"}]
            >>> proj.import_instrument_event_mappings(instrument_event_mappings)
            1
        """
        payload = self._initialize_import_payload(
            to_import=to_import,
            import_format=import_format,
            return_format_type=return_format_type,
            content="formEventMapping",
        )
        payload["action"] = "import"

        return_type = self._lookup_return_type(
            format_type=return_format_type, request_type="import"
        )
        response = cast(Union[Json, str], self._call_api(payload, return_type))

        return response
