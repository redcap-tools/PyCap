"""REDCap API methods for Project users"""
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union, cast

from redcap.methods.base import Base, Json

if TYPE_CHECKING:
    import pandas as pd


class Users(Base):
    """Responsible for all API methods under 'Users & User Privileges' in the API Playground"""

    def export_users(
        self,
        format_type: Literal["json", "csv", "xml", "df"] = "json",
        df_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """
        Export the users of the Project

        Args:
            format_type:
                Response return format
            df_kwargs:
                Passed to `pandas.read_csv` to control construction of
                returned DataFrame. By default, nothing

        Returns:
            Union[List[Dict[str, Any]], str, pandas.DataFrame]: List of users with metadata

        Examples:
            >>> proj.export_users()
            [{'username': ..., 'email': ..., 'expiration': '', 'data_access_group': '',
            'data_access_group_id': '', 'design': 1, 'user_rights': 1, 'data_access_groups': 1,
            'reports': 1, ...}]
        """
        payload = self._initialize_payload(content="user", format_type=format_type)
        return_type = self._lookup_return_type(format_type, request_type="export")
        response = cast(Union[Json, str], self._call_api(payload, return_type))

        return self._return_data(
            response=response,
            content="user",
            format_type=format_type,
            df_kwargs=df_kwargs,
        )

    def import_users(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["json", "csv", "xml"] = "json",
        import_format: Literal["json", "csv", "xml", "df"] = "json",
    ):
        """
        Import users/user rights into the REDCap Project

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
            Union[int, str]: Number of users added or updated

        Examples:
            Add test user. Only username is required
            >>> test_user = [{"username": "pandeharris@gmail.com"}]
            >>> proj.import_users(test_user)
            1

            All currently valid options for user rights
            >>> test_user = [
            ...     {"username": "pandeharris@gmail.com", "email": "pandeharris@gmail.com",
            ...     "firstname": "REDCap Trial", "lastname": "User", "expiration": "",
            ...     "data_access_group": "", "data_access_group_id": "", "design": 0,
            ...     "user_rights": 0, "data_export": 2, "reports": 1, "stats_and_charts": 1,
            ...     "manage_survey_participants": 1, "calendar": 1, "data_access_groups": 0,
            ...     "data_import_tool": 0, "data_comparison_tool": 0, "logging": 0,
            ...     "file_repository": 1, "data_quality_create": 0, "data_quality_execute": 0,
            ...     "api_export": 0, "api_import": 0, "mobile_app": 0,
            ...     "mobile_app_download_data": 0, "record_create": 1, "record_rename": 0,
            ...     "record_delete": 0, "lock_records_all_forms": 0, "lock_records": 0,
            ...      "lock_records_customization": 0, "forms": {"form_1": 3}}
            ... ]
            >>> proj.import_users(test_user)
            1
        """
        payload = self._initialize_import_payload(
            to_import=to_import,
            import_format=import_format,
            return_format_type=return_format_type,
            content="user",
        )

        return_type = self._lookup_return_type(
            format_type=return_format_type, request_type="import"
        )
        response = cast(Union[Json, str], self._call_api(payload, return_type))

        return response

    def delete_users(
        self,
        users: List[str],
        return_format_type: Literal["json", "csv", "xml"] = "json",
    ):
        """
        Delete users from the project.

        Args:
            users: List of usernames to delete from the project
            return_format_type:
                Response format. By default, response will be json-decoded.

        Returns:
            Union[int, str]: Number of users deleted

        Examples:
            >>> new_user = [{"username": "pandeharris@gmail.com"}]
            >>> proj.import_users(new_user)
            1
            >>> proj.delete_users(["pandeharris@gmail.com"], return_format_type="xml")
            '1'
        """
        payload = self._initialize_payload(
            content="user", return_format_type=return_format_type
        )
        payload["action"] = "delete"
        # Turn list of users into dict, and append to payload
        users_dict = {f"users[{ idx }]": user for idx, user in enumerate(users)}
        payload.update(users_dict)

        return_type = self._lookup_return_type(
            format_type=return_format_type, request_type="delete"
        )
        response = cast(Union[Json, str], self._call_api(payload, return_type))
        return response
