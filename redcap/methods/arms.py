"""REDCap API methods for Project arms"""
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union, cast

from redcap.methods.base import Base, Json

if TYPE_CHECKING:
    import pandas as pd


class Arms(Base):
    """Responsible for all API methods under 'Arms' in the API Playground"""

    def export_arms(
        self,
        format_type: Literal["json", "csv", "xml", "df"] = "json",
        df_kwargs: Optional[Dict[str, Any]] = None,
    ):
        # pylint: disable=line-too-long
        """
        Export the Arms of the Project

        Note:
            This only works for longitudinal projects.

        Args:
            format_type:
                Response return format
            df_kwargs:
                Passed to `pandas.read_csv` to control construction of
                returned DataFrame. By default, nothing

        Returns:
            Union[List[Dict[str, Any]], str, pandas.DataFrame]: List of Arms

        Examples:
            >>> proj.export_arms()
            [{'arm_num': 1, 'name': 'Arm 1'}]
        """
        # pylint:enable=line-too-long
        payload = self._initialize_payload(content="arm", format_type=format_type)
        return_type = self._lookup_return_type(format_type, request_type="export")
        response = cast(Union[Json, str], self._call_api(payload, return_type))

        return self._return_data(
            response=response,
            content="arm",
            format_type=format_type,
            df_kwargs=df_kwargs,
        )

    def import_arms(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["json", "csv", "xml"] = "json",
        import_format: Literal["json", "csv", "xml", "df"] = "json",
        override: Optional[int] = 0,
    ):
        """
        Import Arms into the REDCap Project

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
                erase all existing Arms in the project while importing new Arms.
                If override=0, then you can only add new Arms or rename existing ones.

        Returns:
            Union[int, str]: Number of Arms added or updated

        Examples:
            Create a new arm
            >>> new_arm = [{"arm_num": 2, "name": "Arm 2"}]
            >>> proj.import_arms(new_arm)
            1
        """
        payload = self._initialize_import_payload(
            to_import=to_import,
            import_format=import_format,
            return_format_type=return_format_type,
            content="arm",
        )
        payload["action"] = "import"
        payload["override"] = override

        return_type = self._lookup_return_type(
            format_type=return_format_type, request_type="import"
        )
        response = cast(Union[Json, str], self._call_api(payload, return_type))

        return response

    def delete_arms(
        self,
        arms: List[int],
        return_format_type: Literal["json", "csv", "xml"] = "json",
    ):
        """
        Delete Arms from the Project

        Note:
            Because of this method's destructive nature, it is only available
            for use for projects in Development status.
            Additionally, please be aware that deleting an arm also automatically
            deletes all events that belong to that arm, and will also automatically
            delete any records/data that have been collected under that arm
            (this is non-reversible data loss).
            This only works for longitudinal projects.

        Args:
            arms: List of arm numbers to delete from the project
            return_format_type:
                Response format. By default, response will be json-decoded.

        Returns:
            Union[int, str]: Number of arms deleted

        Examples:
            Create a new arm
            >>> new_arm = [{"arm_num": 2, "name": "Arm 2"}]
            >>> proj.import_arms(new_arm)
            1

            Delete the new arm
            >>> proj.delete_arms([2])
            1
        """
        payload = self._initialize_payload(
            content="arm", return_format_type=return_format_type
        )
        payload["action"] = "delete"
        # Turn list of arms into dict, and append to payload
        arms_dict = {f"arms[{ idx }]": arm for idx, arm in enumerate(arms)}
        payload.update(arms_dict)

        return_type = self._lookup_return_type(
            format_type=return_format_type, request_type="delete"
        )
        response = cast(Union[Json, str], self._call_api(payload, return_type))

        return response
