"""REDCap API methods for Project surveys"""
from typing import Dict, List, Optional, overload

from typing_extensions import Literal

from redcap.methods.base import Base


class Surveys(Base):
    """Responsible for all API methods under 'Surveys' in the API Playground"""

    # pylint: disable=redefined-builtin
    @overload
    def export_survey_participant_list(
        self,
        instrument: str,
        format: Literal["json"],
        event: Optional[str] = None,
    ) -> List[Dict]:
        ...

    @overload
    def export_survey_participant_list(
        self,
        instrument: str,
        format: Literal["csv", "xml"],
        event: Optional[str] = None,
    ) -> str:
        ...

    def export_survey_participant_list(
        self,
        instrument: str,
        format: Literal["json", "csv", "xml"] = "json",
        event: Optional[str] = None,
    ):
        """
        Export the Survey Participant List

        Note:
            The passed instrument must be set up as a survey instrument.

        Args:
            instrument:
                Name of instrument as seen in the Data Dictionary (metadata).
            event:
                Unique event name, only used in longitudinal projects
            format:
                Format of returned data

        Returns:
            Union[List[Dict], str]: List of survey participants, along with other useful
            metadata such as the record, response status, etc.
        """
        payload = self._basepl(content="participantList", format=format)
        payload["instrument"] = instrument
        if event:
            payload["event"] = event
        return self._call_api(payload, "exp_survey_participant_list")[0]
        # pylint: enable=redefined-builtin
