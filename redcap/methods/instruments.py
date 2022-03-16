"""REDCap API methods for Project instruments"""
from typing import TYPE_CHECKING, Any, Dict, List, Optional, overload, Union

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

    def export_repeating_instruments_events(
            self,
            format_type: Literal["json", "csv", "xml", "df"] = "json",
            df_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """
        Export the project's repeating instruments and events settings

        Args:
            format_type:
                Return the repeating instruments and events in native objects,
                csv or xml, `'df''` will return a `pandas.DataFrame`
            df_kwargs:
                Passed to pandas.read_csv to control construction of
                returned DataFrame

        Returns:
            Union[str, List[Dict[str, Any]], pd.DataFrame]: Repeating instruments and events
             for the project

        Examples:
            >>> proj.export_repeating_instruments_events()
            [{"form_name":"testform","custom_form_label":""}]
        """
        payload = self._initialize_payload(
            content="repeatingFormsEvents", format_type=format_type
        )

        return_type = self._lookup_return_type(format_type, request_type="export")
        response = self._call_api(payload, return_type)

        return self._return_data(
            response=response,
            content="repeatingFormsEvents",
            format_type=format_type,
            df_kwargs=df_kwargs,
        )

    def import_repeating_instruments_events(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["json", "csv", "xml"] = "json",
        import_format: Literal["json", "csv", "xml", "df"] = "json",
    ):
        """
        Import repeating instrument and event settings into the REDCap Project

        Args:
            to_import: array of dicts, csv/xml string, `pandas.DataFrame`
                Note:
                    If you pass a csv or xml string, you should use the
                    `import format` parameter appropriately.
            return_format_type:
                Response format. By default, response will be json-decoded.
            import_format:
                Format of incoming data. By default, to_import will be json-encoded

        Returns:
            Union[int, str]: The number of repeated instruments activated

        Examples:
            >>> rep_instruments = proj.export_repeating_instruments_events(format_type="csv")
            >>> proj.import_metadata(rep_instruments, import_format="csv")
            1
        """
        payload = self._initialize_import_payload(
            to_import=to_import,
            import_format=import_format,
            return_format_type=return_format_type,
            data_type="repeatingFormsEvents",
        )

        return_type = self._lookup_return_type(
            format_type=return_format_type, request_type="import"
        )
        response = self._call_api(payload, return_type)

        return response
