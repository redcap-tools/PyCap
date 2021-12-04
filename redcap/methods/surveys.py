"""REDCap API methods for Project surveys"""
from redcap.methods.base import Base


class Surveys(Base):
    """Responsible for all API methods under 'Surveys' in the API Playground"""

    # pylint: disable=redefined-builtin
    def export_survey_participant_list(self, instrument, event=None, format="json"):
        """
        Export the Survey Participant List

        Notes
        -----
        The passed instrument must be set up as a survey instrument.

        Parameters
        ----------
        instrument: str
            Name of instrument as seen in second column of Data Dictionary.
        event: str
            Unique event name, only used in longitudinal projects
        format: (json, xml, csv), json by default
            Format of returned data
        """
        payload = self._basepl(content="participantList", format=format)
        payload["instrument"] = instrument
        if event:
            payload["event"] = event
        return self._call_api(payload, "exp_survey_participant_list")[0]
        # pylint: enable=redefined-builtin
