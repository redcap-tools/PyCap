"""REDCap API methods for Project surveys"""
from typing import Optional, overload

from typing_extensions import Literal

from redcap.methods.base import Base, Json


class Surveys(Base):
    """Responsible for all API methods under 'Surveys' in the API Playground"""

    @overload
    def export_survey_participant_list(
        self,
        instrument: str,
        format_type: Literal["json"],
        event: Optional[str] = None,
    ) -> Json:
        ...

    @overload
    def export_survey_participant_list(
        self,
        instrument: str,
        format_type: Literal["csv", "xml"],
        event: Optional[str] = None,
    ) -> str:
        ...

    def export_survey_participant_list(
        self,
        instrument: str,
        format_type: Literal["json", "csv", "xml"] = "json",
        event: Optional[str] = None,
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

        Returns:
            Union[List[Dict[str, Any]], str]: List of survey participants, along with other useful
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

        return_type = self._lookup_return_type(format_type)
        return self._call_api(payload, return_type)
