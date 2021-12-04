"""REDCap API methods for Project users"""
from redcap.methods.base import Base


class Users(Base):
    """Responsible for all API methods under 'Users & User Privileges' in the API Playground"""

    # pylint: disable=redefined-builtin
    def export_users(self, format="json"):
        """
        Export the users of the Project

        Notes
        -----
        Each user will have the following keys:

            * ``'firstname'`` : User's first name
            * ``'lastname'`` : User's last name
            * ``'email'`` : Email address
            * ``'username'`` : User's username
            * ``'expiration'`` : Project access expiration date
            * ``'data_access_group'`` : data access group ID
            * ``'data_export'`` : (0=no access, 2=De-Identified, 1=Full Data Set)
            * ``'forms'`` : a list of dicts with a single key as the form name and
                value is an integer describing that user's form rights,
                where: 0=no access, 1=view records/responses and edit
                records (survey responses are read-only), 2=read only, and
                3=edit survey responses,


        Parameters
        ----------
        format : (``'json'``), ``'csv'``, ``'xml'``
            response return format

        Returns
        -------
        users: list, str
            list of users dicts when ``'format'='json'``,
            otherwise a string
        """
        payload = self._basepl(content="user", format=format)
        return self._call_api(payload, "exp_user")[0]
        # pylint: enable=redefined-builtin
