#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""User facing class for interacting with a REDCap Project"""

from io import StringIO

from redcap.methods.field_names import FieldNames
from redcap.methods.files import Files
from redcap.methods.metadata import Metadata
from redcap.methods.project_info import ProjectInfo
from redcap.methods.records import Records
from redcap.methods.reports import Reports


__author__ = "Scott Burns <scott.s.burnsgmail.com>"
__license__ = "MIT"
__copyright__ = "2014, Vanderbilt University"

# pylint: disable=too-many-lines
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
# pylint: disable=too-many-public-methods
# pylint: disable=redefined-builtin
# pylint: disable=consider-using-f-string
# pylint: disable=consider-using-generator
# pylint: disable=use-dict-literal
class Project(FieldNames, Files, Metadata, ProjectInfo, Records, Reports):
    """Main class for interacting with REDCap projects"""

    def export_fem(self, arms=None, format="json", df_kwargs=None):
        """
        Export the project's form to event mapping

        Parameters
        ----------
        arms : list
            Limit exported form event mappings to these arm numbers
        format : (``'json'``), ``'csv'``, ``'xml'``
            Return the form event mappings in native objects,
            csv or xml, ``'df''`` will return a ``pandas.DataFrame``
        df_kwargs : dict
            Passed to pandas.read_csv to control construction of
            returned DataFrame

        Returns
        -------
        fem : list, str, ``pandas.DataFrame``
            form-event mapping for the project
        """
        ret_format = format
        if format == "df":
            ret_format = "csv"
        payload = self._basepl("formEventMapping", format=ret_format)

        if arms:
            for i, value in enumerate(arms):
                payload["arms[{}]".format(i)] = value

        response, _ = self._call_api(payload, "exp_fem")
        if format in ("json", "csv", "xml"):
            return response
        if format != "df":
            raise ValueError(("Unsupported format: '{}'").format(format))
        if not df_kwargs:
            df_kwargs = {}

        return self.read_csv(StringIO(response), **df_kwargs)

    def metadata_type(self, field_name):
        """If the given field_name is validated by REDCap, return it's type"""
        return self._meta_metadata(
            field_name, "text_validation_type_or_show_slider_number"
        )

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


# pylint: enable=too-many-instance-attributes
# pylint: enable=too-many-arguments
# pylint: enable=too-many-public-methods
# pylint: enable=redefined-builtin
