"""REDCap API methods for Project users"""
from typing import overload

from typing_extensions import Literal

from redcap.methods.base import Base, Json


class Users(Base):
    """Responsible for all API methods under 'Users & User Privileges' in the API Playground"""

    @overload
    def export_users(self, format_type: Literal["json"]) -> Json:
        ...

    @overload
    def export_users(self, format_type: Literal["csv", "xml"]) -> str:
        ...

    def export_users(self, format_type: Literal["json", "csv", "xml"] = "json"):
        """
        Export the users of the Project

        Note:
            Each user will have the following keys:

                * `'firstname'` : User's first name
                * `'lastname'` : User's last name
                * `'email'` : Email address
                * `'username'` : User's username
                * `'expiration'` : Project access expiration date
                * `'data_access_group'` : data access group ID
                * `'data_export'` : (0=no access, 2=De-Identified, 1=Full Data Set)
                * `'forms'` : a list of dicts with a single key as the form name and
                    value is an integer describing that user's form rights,
                    where: 0=no access, 1=view records/responses and edit
                    records (survey responses are read-only), 2=read only, and
                    3=edit survey responses,

        Args:
            format_type:
                Response return format

        Returns:
            Union[List[Dict[str, Any]], str]: List of users with metadata

        Examples:
            >>> proj.export_users()
            [{'username': ..., 'email': ..., 'expiration': '', 'data_access_group': '',
            'data_access_group_id': '', 'design': 1, 'user_rights': 1, 'data_access_groups': 1,
            'data_export': 1, ...}]
        """
        payload = self._initialize_payload(content="user", format_type=format_type)
        return_type = self._lookup_return_type(format_type)
        return self._call_api(payload, return_type)
