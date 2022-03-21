"""REDCap API methods for Project surveys"""
from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, overload

from redcap.methods.base import Base, Json

if TYPE_CHECKING:
    import pandas as pd


class Surveys(Base):
    """Responsible for all API methods under 'Surveys' in the API Playground"""

    @overload
    def export_survey_participant_list(
        self,
        instrument: str,
        format_type: Literal["json"],
        event: Optional[str],
        df_kwargs: None,
    ) -> Json:
        ...

    @overload
    def export_survey_participant_list(
        self,
        instrument: str,
        format_type: Literal["csv", "xml"],
        event: Optional[str],
        df_kwargs: None,
    ) -> str:
        ...

    @overload
    def export_survey_participant_list(
        self,
        instrument: str,
        format_type: Literal["df"],
        event: Optional[str] = None,
        df_kwargs: Optional[Dict[str, Any]] = None,
    ) -> "pd.DataFrame":
        ...

    def export_survey_participant_list(
        self,
        instrument: str,
        format_type: Literal["json", "csv", "xml", "df"] = "json",
        event: Optional[str] = None,
        df_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """
        Export the Survey Participant List

        Note:
            The passed instrument must be set up as a survey instrument.

        Args:
            instrument:
                Name of instrument as seen in the Data Dictionary (metadata).
            format_type:
                Format of returned data
            event:
                Unique event name, only used in longitudinal projects
            df_kwargs:
                Passed to `pandas.read_csv` to control construction of
                returned DataFrame. By default, nothing

        Returns:
            Union[List[Dict[str, Any]], str, pandas.DataFrame]:
                List of survey participants,
                along with other useful
                metadata such as the record, response status, etc.

        Examples:
            >>> proj.export_survey_participant_list(instrument="form_1", event="event_1_arm_1")
            [{'email': '',
            ...
            'survey_access_code': ...},
            {'email': '',
            ...
            'survey_access_code': ...}]
        """
        payload = self._initialize_payload(
            content="participantList", format_type=format_type
        )
        payload["instrument"] = instrument
        if event:
            payload["event"] = event

        return_type = self._lookup_return_type(format_type, request_type="export")
        response = self._call_api(payload, return_type)

        return self._return_data(
            response=response,
            content="participantList",
            format_type=format_type,
            df_kwargs=df_kwargs,
        )
