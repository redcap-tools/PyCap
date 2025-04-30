"""REDCap API methods for Project surveys"""

from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, Union, cast

from redcap.methods.base import Base, Json

if TYPE_CHECKING:
    import pandas as pd


class Surveys(Base):
    """Responsible for all API methods under 'Surveys' in the API Playground"""

    def export_survey_link(
        self,
        record: str,
        instrument: str,
        event: Optional[str] = None,
        repeat_instance: int = 1,
    ) -> str:
        """
        Export one survey link

        Note:
            The passed instrument must be set up as a survey instrument.

        Args:
            record:
                Name of the record
            instrument:
                Name of instrument as seen in the Data Dictionary (metadata).
            event:
                Unique event name, only used in longitudinal projects
            repeat_instance:
                only for projects with repeating instruments/events)
                The repeat instance number of the repeating event (if longitudinal)
                or the repeating instrument (if classic or longitudinal).
                Default value is '1'.

        Returns:
            URL of survey link requested

        Examples:
            >>> proj.export_survey_link(record="1", instrument="form_1", event="event_1_arm_1")
            'https://redcapdemo.vumc.org/surveys/?s=...'
        """
        payload = self._initialize_payload(
            content="surveyLink",
            # Hard-coded due to the nature of the response
            return_format_type="csv",
        )

        payload["record"] = record
        payload["instrument"] = instrument
        payload["repeat_instance"] = repeat_instance

        if event:
            payload["event"] = event

        return cast(str, self._call_api(payload, return_type="str"))

    def export_survey_access_code(
        self,
        record: str,
        instrument: str,
        event: Optional[str] = None,
        repeat_instance: int = 1,
    ) -> str:
        # pylint: disable=line-too-long
        """
        Export a Survey Access Code for a Participant

        Note:
            The passed instrument must be set up as a survey instrument.

        Args:
            record:
                Name of the record
            instrument:
                Name of instrument as seen in the Data Dictionary (metadata).
            event:
                Unique event name, only used in longitudinal projects
            repeat_instance:
                only for projects with repeating instruments/events)
                The repeat instance number of the repeating event (if longitudinal)
                or the repeating instrument (if classic or longitudinal).
                Default value is '1'.

        Returns:
            A survey access code for a specified record and data collection
            instrument

        Examples:
            >>> proj.export_survey_access_code(record="1", instrument="form_1", event="event_1_arm_1")
            '...'
        """
        # pylint: enable=line-too-long
        payload = self._initialize_payload(
            content="surveyAccessCode",
            # Hard-coded due to the nature of the response
            return_format_type="csv",
        )

        payload["record"] = record
        payload["instrument"] = instrument
        payload["repeat_instance"] = repeat_instance

        if event:
            payload["event"] = event

        return cast(str, self._call_api(payload, return_type="str"))

    def export_survey_participant_list(
        self,
        instrument: str,
        format_type: Literal["json", "csv", "xml", "df"] = "json",
        event: Optional[str] = None,
        df_kwargs: Optional[Dict[str, Any]] = None,
        #return_format_type: Literal["json", "csv", "xml"] = "json",
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
            content="participantList",
            format_type=format_type,
        )
        payload["instrument"] = instrument
        if event:
            payload["event"] = event

        return_type = self._lookup_return_type(format_type, request_type="export")
        response = cast(Union[Json, str], self._call_api(payload, return_type))

        return self._return_data(
            response=response,
            content="participantList",
            format_type=format_type,
            df_kwargs=df_kwargs,
        )
