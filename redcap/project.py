#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""User facing class for interacting with a REDCap Project"""

from io import StringIO

from redcap.request import RedcapError
from redcap.methods.field_names import FieldNames
from redcap.methods.files import Files
from redcap.methods.metadata import Metadata


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
class Project(FieldNames, Files, Metadata):
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

    def delete_records(self, records):
        """
        Delete records from the Project.

        Parameters
        ----------
        records : list
            List of record IDs that you want to delete from the project

        Returns
        -------
        response : int
            Number of records deleted
        """
        payload = dict()
        payload["action"] = "delete"
        payload["content"] = "record"
        payload["token"] = self.token
        # Turn list of records into dict, and append to payload
        records_dict = {
            "records[{}]".format(idx): record for idx, record in enumerate(records)
        }
        payload.update(records_dict)

        payload["format"] = format
        response, _ = self._call_api(payload, "del_record")
        return response

    # pylint: disable=too-many-branches
    # pylint: disable=too-many-locals
    def export_records(
        self,
        records=None,
        fields=None,
        forms=None,
        events=None,
        raw_or_label="raw",
        event_name="label",
        type="flat",
        format="json",
        export_survey_fields=False,
        export_data_access_groups=False,
        df_kwargs=None,
        export_checkbox_labels=False,
        filter_logic=None,
        date_begin=None,
        date_end=None,
    ):
        """
        Export data from the REDCap project.

        Parameters
        ----------
        records : list
            array of record names specifying specific records to export.
            by default, all records are exported
        fields : list
            array of field names specifying specific fields to pull
            by default, all fields are exported
        forms : list
            array of form names to export. If in the web UI, the form
            name has a space in it, replace the space with an underscore
            by default, all forms are exported
        events : list
            an array of unique event names from which to export records

            :note: this only applies to longitudinal projects
        raw_or_label : (``'raw'``), ``'label'``, ``'both'``
            export the raw coded values or labels for the options of
            multiple choice fields, or both
        event_name : (``'label'``), ``'unique'``
             export the unique event name or the event label
        type : (``'flat'``), ``'eav'``
             database output structure type
        format : (``'json'``), ``'csv'``, ``'xml'``, ``'df'``
            Format of returned data. ``'json'`` returns json-decoded
            objects while ``'csv'`` and ``'xml'`` return other formats.
            ``'df'`` will attempt to return a ``pandas.DataFrame``.
        export_survey_fields : (``False``), True
            specifies whether or not to export the survey identifier
            field (e.g., "redcap_survey_identifier") or survey timestamp
            fields (e.g., form_name+"_timestamp") when surveys are
            utilized in the project.
        export_data_access_groups : (``False``), ``True``
            specifies whether or not to export the
            ``"redcap_data_access_group"`` field when data access groups
            are utilized in the project.

            :note: This flag is only viable if the user whose token is
                being used to make the API request is *not* in a data
                access group. If the user is in a group, then this flag
                will revert to its default value.
        df_kwargs : dict
            Passed to ``pandas.read_csv`` to control construction of
            returned DataFrame.
            by default, ``{'index_col': self.def_field}``
        export_checkbox_labels : (``False``), ``True``
            specify whether to export checkbox values as their label on
            export.
        filter_logic : string
            specify the filterLogic to be sent to the API.
        date_begin : datetime
            for the dateRangeBegin filtering of the API
        date_end : datetime
            for the dateRangeEnd filtering snet to the API

        Returns
        -------
        data : list, str, ``pandas.DataFrame``
            exported data
        """
        ret_format = format
        if format == "df":
            ret_format = "csv"
        payload = self._basepl("record", format=ret_format, rec_type=type)
        fields = self.backfill_fields(fields, forms)
        keys_to_add = (
            records,
            fields,
            forms,
            events,
            raw_or_label,
            event_name,
            export_survey_fields,
            export_data_access_groups,
            export_checkbox_labels,
        )

        str_keys = (
            "records",
            "fields",
            "forms",
            "events",
            "rawOrLabel",
            "eventName",
            "exportSurveyFields",
            "exportDataAccessGroups",
            "exportCheckboxLabel",
        )

        if export_survey_fields:
            fields.extend([name + "_complete" for name in self.forms])

        for key, data in zip(str_keys, keys_to_add):
            if data:
                if key in ("fields", "records", "forms", "events"):
                    for i, value in enumerate(data):
                        payload["{}[{}]".format(key, i)] = value
                else:
                    payload[key] = data

        if date_begin:
            payload["dateRangeBegin"] = date_begin.strftime("%Y-%m-%d %H:%M:%S")

        if date_end:
            payload["dateRangeEnd"] = date_end.strftime("%Y-%m-%d %H:%M:%S")

        if filter_logic:
            payload["filterLogic"] = filter_logic
        response, _ = self._call_api(payload, "exp_record")
        if format in ("json", "csv", "xml"):
            return response
        if format != "df":
            raise ValueError(("Unsupported format: '{}'").format(format))

        if not df_kwargs:
            if type == "eav":
                df_kwargs = {}
            else:
                if self.is_longitudinal():
                    df_kwargs = {"index_col": [self.def_field, "redcap_event_name"]}
                else:
                    df_kwargs = {"index_col": self.def_field}
        buf = StringIO(response)
        dataframe = self.read_csv(buf, **df_kwargs)
        buf.close()

        return dataframe

    # pylint: enable=too-many-branches
    # pylint: enable=too-many-locals

    def metadata_type(self, field_name):
        """If the given field_name is validated by REDCap, return it's type"""
        return self._meta_metadata(
            field_name, "text_validation_type_or_show_slider_number"
        )

    def backfill_fields(self, fields, forms):
        """
        Properly backfill fields to explicitly request specific
        keys. The issue is that >6.X servers *only* return requested fields
        so to improve backwards compatiblity for PyCap clients, add specific fields
        when required.

        Parameters
        ----------
        fields: list
            requested fields
        forms: list
            requested forms

        Returns
        -------
            new fields, forms
        """
        if forms and not fields:
            new_fields = [self.def_field]
        elif fields and self.def_field not in fields:
            new_fields = list(fields)
            if self.def_field not in fields:
                new_fields.append(self.def_field)
        elif not fields:
            new_fields = self.field_names
        else:
            new_fields = list(fields)
        return new_fields

    def import_records(
        self,
        to_import,
        overwrite="normal",
        format="json",
        return_format="json",
        return_content="count",
        date_format="YMD",
        force_auto_number=False,
    ):
        """
        Import data into the RedCap Project

        Parameters
        ----------
        to_import : array of dicts, csv/xml string, ``pandas.DataFrame``
            :note:
                If you pass a csv or xml string, you should use the
                ``format`` parameter appropriately.
            :note:
                Keys of the dictionaries should be subset of project's,
                fields, but this isn't a requirement. If you provide keys
                that aren't defined fields, the returned response will
                contain an ``'error'`` key.
        overwrite : ('normal'), 'overwrite'
            ``'overwrite'`` will erase values previously stored in the
            database if not specified in the to_import dictionaries.
        format : ('json'),  'xml', 'csv'
            Format of incoming data. By default, to_import will be json-encoded
        return_format : ('json'), 'csv', 'xml'
            Response format. By default, response will be json-decoded.
        return_content : ('count'), 'ids', 'nothing'
            By default, the response contains a 'count' key with the number of
            records just imported. By specifying 'ids', a list of ids
            imported will be returned. 'nothing' will only return
            the HTTP status code and no message.
        date_format : ('YMD'), 'DMY', 'MDY'
            Describes the formatting of dates. By default, date strings
            are formatted as 'YYYY-MM-DD' corresponding to 'YMD'. If date
            strings are formatted as 'MM/DD/YYYY' set this parameter as
            'MDY' and if formatted as 'DD/MM/YYYY' set as 'DMY'. No
            other formattings are allowed.
        force_auto_number : ('False') Enables automatic assignment of record IDs
            of imported records by REDCap. If this is set to true, and auto-numbering
            for records is enabled for the project, auto-numbering of imported records
            will be enabled.

        Returns
        -------
        response : dict, str
            response from REDCap API, json-decoded if ``return_format`` == ``'json'``
        """
        payload = self._initialize_import_payload(to_import, format, "record")

        payload["overwriteBehavior"] = overwrite
        payload["returnFormat"] = return_format
        payload["returnContent"] = return_content
        payload["dateFormat"] = date_format
        payload["forceAutoNumber"] = force_auto_number
        response = self._call_api(payload, "imp_record")[0]
        if "error" in response:
            raise RedcapError(str(response))
        return response

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

    def generate_next_record_name(self):
        """Return the next record name for auto-numbering records"""
        payload = self._basepl(content="generateNextRecordName")

        return self._call_api(payload, "exp_next_id")[0]

    def export_project_info(self, format="json"):
        """
        Export Project Information

        Parameters
        ----------
        format: (json, xml, csv), json by default
            Format of returned data
        """

        payload = self._basepl(content="project", format=format)

        return self._call_api(payload, "exp_proj")[0]

    # pylint: disable=too-many-locals
    def export_reports(
        self,
        format="json",
        report_id=None,
        raw_or_label="raw",
        raw_or_label_headers="raw",
        export_checkbox_labels="false",
        decimal_character=None,
        df_kwargs=None,
    ):
        """
        Export a report of the Project

        Notes
        -----


        Parameters
        ----------
        report_id : the report ID number provided next to the report name
            on the report list page
        format :  (``'json'``), ``'csv'``, ``'xml'``, ``'df'``
            Format of returned data. ``'json'`` returns json-decoded
            objects while ``'csv'`` and ``'xml'`` return other formats.
            ``'df'`` will attempt to return a ``pandas.DataFrame``.
        raw_or_label : raw [default], label - export the raw coded values or
            labels for the options of multiple choice fields
        raw_or_label_headers : raw [default], label - (for 'csv' format 'flat'
            type only) for the CSV headers, export the variable/field names
            (raw) or the field labels (label)
        export_checkbox_labels : true, false [default] - specifies the format of
            checkbox field values specifically when exporting the data as labels
            (i.e., when rawOrLabel=label). When exporting labels, by default
            (without providing the exportCheckboxLabel flag or if
            exportCheckboxLabel=false), all checkboxes will either have a value
            'Checked' if they are checked or 'Unchecked' if not checked.
            But if exportCheckboxLabel is set to true, it will instead export
            the checkbox value as the checkbox option's label (e.g., 'Choice 1')
            if checked or it will be blank/empty (no value) if not checked.
            If rawOrLabel=false, then the exportCheckboxLabel flag is ignored.
        decimal_character : If specified, force all numbers into same decimal
            format. You may choose to force all data values containing a
            decimal to have the same decimal character, which will be applied
            to all calc fields and number-validated text fields. Options
            include comma ',' or dot/full stop '.', but if left blank/null,
            then it will export numbers using the fields' native decimal format.
            Simply provide the value of either ',' or '.' for this parameter.

        Returns
        -------
        Per Redcap API:
        Data from the project in the format and type specified
        Ordered by the record (primary key of project) and then by event id
        """

        ret_format = format
        if format == "df":
            ret_format = "csv"

        payload = self._basepl(content="report", format=ret_format)
        keys_to_add = (
            report_id,
            raw_or_label,
            raw_or_label_headers,
            export_checkbox_labels,
            decimal_character,
        )
        str_keys = (
            "report_id",
            "rawOrLabel",
            "rawOrLabelHeaders",
            "exportCheckboxLabel",
            "decimalCharacter",
        )
        for key, data in zip(str_keys, keys_to_add):
            if data:
                payload[key] = data
        response, _ = self._call_api(payload, "exp_report")
        if format in ("json", "csv", "xml"):
            return response
        if format != "df":
            raise ValueError(("Unsupported format: '{}'").format(format))

        if not df_kwargs:
            if self.is_longitudinal():
                df_kwargs = {"index_col": [self.def_field, "redcap_event_name"]}
            else:
                df_kwargs = {"index_col": self.def_field}
        buf = StringIO(response)
        dataframe = self.read_csv(buf, **df_kwargs)
        buf.close()

        return dataframe

    # pylint: enable=too-many-locals


# pylint: enable=too-many-instance-attributes
# pylint: enable=too-many-arguments
# pylint: enable=too-many-public-methods
# pylint: enable=redefined-builtin
