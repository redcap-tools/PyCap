"""REDCap API methods for Project events"""
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union, cast

from redcap.methods.base import Base, Json

if TYPE_CHECKING:
    import pandas as pd


class Events(Base):
    """Responsible for all API methods under 'Events' in the API Playground"""

    def export_events(
        self,
        format_type: Literal["json", "csv", "xml", "df"] = "json",
        arms: Optional[List[str]] = None,
    ):
        # pylint: disable=line-too-long
        """
        Export the Events of the Project

        Note:
            This only works for longitudinal projects.

        Args:
            format_type:
                Response return format
            arms:
                An array of arm numbers that you wish to pull events for
                (by default, all events are pulled)

        Returns:
            Union[List[Dict[str, Any]], str, pandas.DataFrame]: List of Events

        Examples:
            >>> proj.export_events()
            [{"event_name": "Event 1", "arm_num": 1, "unique_event_name": "event_1_arm_1",
            "custom_event_label": null, "event_id": 1}]
        """
        # pylint:enable=line-too-long
        payload = self._initialize_payload(content="event", format_type=format_type)
        if arms:
            # Turn list of arms into dict, and append to payload
            arms_dict = {f"arms[{ idx }]": arm for idx, arm in enumerate(arms)}
            payload.update(arms_dict)
        return_type = self._lookup_return_type(format_type, request_type="export")
        response = cast(Union[Json, str], self._call_api(payload, return_type))

        return self._return_data(
            response=response,
            content="event",
            format_type=format_type,
        )

    def import_events(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["json", "csv", "xml"] = "json",
        import_format: Literal["json", "csv", "xml", "df"] = "json",
        override: Optional[int] = 0,
    ):
        """
        Import Events into the REDCap Project

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
                Format of incoming data. By default, to_import will be json-encoded
            override:
                0 - false [default], 1 - true
                You may use override=1 as a 'delete all + import' action in order to
                erase all existing Events in the project while importing new Events.
                If override=0, then you can only add new Events or rename existing ones.

        Returns:
            Union[int, str]: Number of Events added or updated

        Examples:
            Create a new event
            >>> new_event = [{"event_name": "Event 2", "arm_num": "1"}]
            >>> proj.import_events(new_event)
            1
        """
        payload = self._initialize_import_payload(
            to_import=to_import,
            import_format=import_format,
            return_format_type=return_format_type,
            content="event",
        )
        payload["action"] = "import"
        payload["override"] = override

        return_type = self._lookup_return_type(
            format_type=return_format_type, request_type="import"
        )
        response = cast(Union[Json, str], self._call_api(payload, return_type))

        return response

    def delete_events(
        self,
        events: List[str],
        return_format_type: Literal["json", "csv", "xml"] = "json",
    ):
        """
        Delete Events from the Project

        Note:
            Because of this method's destructive nature, it is only available
            for use for projects in Development status.
            Additionally, please be aware that deleting an event will automatically
            delete any records/data that have been collected under that event
            (this is non-reversible data loss).
            This only works for longitudinal projects.

        Args:
            events: List of unique event names to delete from the project
            return_format_type:
                Response format. By default, response will be json-decoded.

        Returns:
            Union[int, str]: Number of events deleted

        Examples:
            Create a new event
            >>> new_event = [{"event_name": "Event 2", "arm_num": "1"}]
            >>> proj.import_events(new_event)
            1

            Delete the new event
            >>> proj.delete_events(["event_2_arm_1"])
            1
        """
        payload = self._initialize_payload(
            content="event", return_format_type=return_format_type
        )
        payload["action"] = "delete"
        # Turn list of events into dict, and append to payload
        events_dict = {f"events[{ idx }]": event for idx, event in enumerate(events)}
        payload.update(events_dict)

        return_type = self._lookup_return_type(
            format_type=return_format_type, request_type="delete"
        )
        response = cast(Union[Json, str], self._call_api(payload, return_type))

        return response
