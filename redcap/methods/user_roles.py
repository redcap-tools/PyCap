"""REDCap API methods for Project user roles"""
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union, overload

from redcap.methods.base import Base, Json

if TYPE_CHECKING:
    import pandas as pd


class UserRoles(Base):
    """Responsible for all API methods under 'Users Roles' in the API Playground"""

    @overload
    def export_user_roles(self, format_type: Literal["json"], df_kwargs: None) -> Json:
        ...

    @overload
    def export_user_roles(
        self, format_type: Literal["csv", "xml"], df_kwargs: None
    ) -> str:
        ...

    @overload
    def export_user_roles(
        self, format_type: Literal["df"], df_kwargs: Optional[Dict[str, Any]]
    ) -> "pd.DataFrame":
        ...

    def export_user_roles(
        self,
        format_type: Literal["json", "csv", "xml", "df"] = "json",
        df_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """
        Export the user roles of the Project

        Args:
            format_type:
                Response return format
            df_kwargs:
                Passed to `pandas.read_csv` to control construction of
                returned DataFrame. By default, nothing

        Returns:
            Union[List[Dict[str, Any]], str, pandas.DataFrame]:
                List of user roles with assigned user rights

        Examples:
            >>> proj.export_user_roles()
            [{'unique_role_name': ..., 'role_label': 'Test role', 'design': '0', 'user_rights': '0',
            'data_access_groups': '0', 'reports': '0', 'stats_and_charts': '0',
            'manage_survey_participants': '0', 'calendar': '0', 'data_import_tool': '0',
            'data_comparison_tool': '0', 'logging': '0', 'file_repository': '0',
            'data_quality_create': '0', 'data_quality_execute': '0', 'api_export': '0',
            'api_import': '0', 'mobile_app': '0', 'mobile_app_download_data': '0',
            'record_create': '0', 'record_rename': '0', 'record_delete': '0',
            'lock_records_customization': '0', 'lock_records': '0', ...,
            'forms': {'form_1': 2}, 'forms_export': {'form_1': 0}}]
        """
        payload = self._initialize_payload(content="userRole", format_type=format_type)
        return_type = self._lookup_return_type(format_type, request_type="export")
        response = self._call_api(payload, return_type)

        return self._return_data(
            response=response,
            content="userRole",
            format_type=format_type,
            df_kwargs=df_kwargs,
        )

    @overload
    def import_user_roles(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["json"],
        import_format: Literal["json", "csv", "xml", "df"] = "json",
    ) -> int:
        ...

    @overload
    def import_user_roles(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["csv", "xml"],
        import_format: Literal["json", "csv", "xml", "df"] = "json",
    ) -> str:
        ...

    def import_user_roles(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["json", "csv", "xml"] = "json",
        import_format: Literal["json", "csv", "xml", "df"] = "json",
    ):
        """
        Import user roles into the REDCap Project

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
            Union[int, str]: Number of user roles added or updated

        Examples:
            >>> roles = proj.export_user_roles()
            >>> proj.import_user_roles(roles)
            1
        """
        payload = self._initialize_import_payload(
            to_import=to_import,
            import_format=import_format,
            return_format_type=return_format_type,
            content="userRole",
        )

        return_type = self._lookup_return_type(
            format_type=return_format_type, request_type="import"
        )
        response = self._call_api(payload, return_type)

        return response

    @overload
    def export_user_role_assignment(
        self, format_type: Literal["json"], df_kwargs: None
    ) -> Json:
        ...

    @overload
    def export_user_role_assignment(
        self, format_type: Literal["csv", "xml"], df_kwargs: None
    ) -> str:
        ...

    @overload
    def export_user_role_assignment(
        self, format_type: Literal["df"], df_kwargs: Optional[Dict[str, Any]]
    ) -> "pd.DataFrame":
        ...

    def export_user_role_assignment(
        self,
        format_type: Literal["json", "csv", "xml", "df"] = "json",
        df_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """
        Export the User-Role assignments of the Project

        Args:
            format_type:
                Response return format
            df_kwargs:
                Passed to `pandas.read_csv` to control construction of
                returned DataFrame. By default, nothing

        Returns:
            Union[List[Dict[str, Any]], str, pandas.DataFrame]:
                List of user-role assignments

        Examples:
            >>> proj.export_user_role_assignment()
            [{'username': ..., 'unique_role_name': ''}]
        """
        payload = self._initialize_payload(
            content="userRoleMapping", format_type=format_type
        )
        return_type = self._lookup_return_type(format_type, request_type="export")
        response = self._call_api(payload, return_type)

        return self._return_data(
            response=response,
            content="userRoleMapping",
            format_type=format_type,
            df_kwargs=df_kwargs,
        )

    @overload
    def import_user_role_assignment(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["json"],
        import_format: Literal["json", "csv", "xml", "df"] = "json",
    ) -> int:
        ...

    @overload
    def import_user_role_assignment(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["csv", "xml"],
        import_format: Literal["json", "csv", "xml", "df"] = "json",
    ) -> str:
        ...

    def import_user_role_assignment(
        self,
        to_import: Union[str, List[Dict[str, Any]], "pd.DataFrame"],
        return_format_type: Literal["json", "csv", "xml"] = "json",
        import_format: Literal["json", "csv", "xml", "df"] = "json",
    ):
        """
        Import User-Role assignments into the REDCap Project

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
            Union[int, str]: Number of user-role assignments added or updated

        Examples:
            >>> user_role_assignments = proj.export_user_role_assignment()
            >>> proj.import_user_role_assignment(user_role_assignments)
            1
        """
        payload = self._initialize_import_payload(
            to_import=to_import,
            import_format=import_format,
            return_format_type=return_format_type,
            content="userRoleMapping",
        )

        return_type = self._lookup_return_type(
            format_type=return_format_type, request_type="import"
        )
        response = self._call_api(payload, return_type)

        return response
