"""REDCap API methods for Project repeating instruments"""
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, Literal, cast

from redcap.methods.base import Base
from redcap.request import Json

if TYPE_CHECKING:
    import pandas as pd


class Repeating(Base):
    """Responsible for all API methods under 'Repeating Instruments and Events'
    in the API Playground
    """

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
            [{'event_name': 'event_1_arm_1', 'form_name': '', 'custom_form_label': ''}]
        """
        payload = self._initialize_payload(
            content="repeatingFormsEvents", format_type=format_type
        )

        return_type = self._lookup_return_type(format_type, request_type="export")
        response = cast(Union[Json, str], self._call_api(payload, return_type))

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
            >>> proj.import_repeating_instruments_events(rep_instruments, import_format="csv")
            1
        """
        payload = self._initialize_import_payload(
            to_import=to_import,
            import_format=import_format,
            return_format_type=return_format_type,
            content="repeatingFormsEvents",
        )

        return_type = self._lookup_return_type(
            format_type=return_format_type, request_type="import"
        )
        response = cast(Union[Json, str], self._call_api(payload, return_type))

        return response
