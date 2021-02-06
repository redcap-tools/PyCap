#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""User facing class for interacting with a REDCap Project"""

import json
import warnings
import semantic_version

from .request import RCRequest, RedcapError, RequestException

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

__author__ = "Scott Burns <scott.s.burnsgmail.com>"
__license__ = "MIT"
__copyright__ = "2014, Vanderbilt University"

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
# pylint: disable=too-many-public-methods
# pylint: disable=redefined-builtin
class Project(object):
    """Main class for interacting with REDCap projects"""

    def __init__(self, url, token, name="", verify_ssl=True, lazy=False):
        """
        Parameters
        ----------
        url : str
            API URL to your REDCap server
        token : str
            API token to your project
        name : str, optional
            name for project
        verify_ssl : boolean, str
            Verify SSL, default True. Can pass path to CA_BUNDLE.
        """

        self.token = token
        self.name = name
        self.url = url
        self.verify = verify_ssl
        self.metadata = None
        self.redcap_version = None
        self.field_names = None
        # We'll use the first field as the default id for each row
        self.def_field = None
        self.field_labels = None
        self.forms = None
        self.events = None
        self.arm_nums = None
        self.arm_names = None
        self.configured = False

        if not lazy:
            self.configure()

    def configure(self):
        """Fill in project attributes"""
        try:
            self.metadata = self.__md()
        except RequestException as request_fail:
            raise RedcapError(
                "Exporting metadata failed. Check your URL and token."
            ) from request_fail
        try:
            self.redcap_version = self.__rcv()
        except Exception as general_fail:
            raise RedcapError(
                "Determination of REDCap version failed"
            ) from general_fail
        self.field_names = self.filter_metadata("field_name")
        # we'll use the first field as the default id for each row
        self.def_field = self.field_names[0]
        self.field_labels = self.filter_metadata("field_label")
        self.forms = tuple(set(c["form_name"] for c in self.metadata))
        # determine whether longitudinal
        ev_data = self._call_api(self.__basepl("event"), "exp_event")[0]
        arm_data = self._call_api(self.__basepl("arm"), "exp_arm")[0]

        if isinstance(ev_data, dict) and ("error" in ev_data.keys()):
            events = tuple([])
        else:
            events = ev_data

        if isinstance(arm_data, dict) and ("error" in arm_data.keys()):
            arm_nums = tuple([])
            arm_names = tuple([])
        else:
            arm_nums = tuple([a["arm_num"] for a in arm_data])
            arm_names = tuple([a["name"] for a in arm_data])
        self.events = events
        self.arm_nums = arm_nums
        self.arm_names = arm_names
        self.configured = True

    def __md(self):
        """Return the project's metadata structure"""
        p_l = self.__basepl("metadata")
        p_l["content"] = "metadata"
        return self._call_api(p_l, "metadata")[0]

    def __basepl(self, content, rec_type="flat", format="json"):
        """Return a dictionary which can be used as is or added to for
        payloads"""
        payload_dict = {"token": self.token, "content": content, "format": format}
        if content not in ["metapayload_dictata", "file"]:
            payload_dict["type"] = rec_type
        return payload_dict

    def __rcv(self):
        payload = self.__basepl("version")
        rcv = self._call_api(payload, "version")[0].decode("utf-8")
        if "error" in rcv:
            warnings.warn("Version information not available for this REDCap instance")
            return ""
        if semantic_version.validate(rcv):
            return semantic_version.Version(rcv)

        return rcv

    def is_longitudinal(self):
        """
        Returns
        -------
        boolean :
            longitudinal status of this project
        """
        return (
            len(self.events) > 0 and len(self.arm_nums) > 0 and len(self.arm_names) > 0
        )

    def filter_metadata(self, key):
        """
        Return a list of values for the metadata key from each field
        of the project's metadata.

        Parameters
        ----------
        key: str
            A known key in the metadata structure

        Returns
        -------
        filtered :
            attribute list from each field
        """
        filtered = [field[key] for field in self.metadata if key in field]
        if len(filtered) == 0:
            raise KeyError("Key not found in metadata")
        return filtered

    def _kwargs(self):
        """Private method to build a dict for sending to RCRequest

        Other default kwargs to the http library should go here"""
        return {"verify": self.verify}

    def _call_api(self, payload, typpe, **kwargs):
        request_kwargs = self._kwargs()
        request_kwargs.update(kwargs)
        rcr = RCRequest(self.url, payload, typpe)
        return rcr.execute(**request_kwargs)

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
        payload = self.__basepl("formEventMapping", format=ret_format)

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

    def export_field_names(self, field=None, format="json", df_kwargs=None):
        """
        Export the project's export field names

        Parameters
        ----------
        fields : str
            Limit exported field name to this field (only single field supported).
            When not provided, all fields returned.
        format : (``'json'``), ``'csv'``, ``'xml'``, ``'df'``
            Return the metadata in native objects, csv or xml.
            ``'df'`` will return a ``pandas.DataFrame``.
        df_kwargs : dict
            Passed to ``pandas.read_csv`` to control construction of
            returned DataFrame.
            by default ``{'index_col': 'original_field_name'}``

        Returns
        -------
        metadata : list, str, ``pandas.DataFrame``
            metadata structure for the project.
        """
        ret_format = format
        if format == "df":
            ret_format = "csv"

        payload = self.__basepl("exportFieldNames", format=ret_format)

        if field:
            payload["field"] = field

        response, _ = self._call_api(payload, "exp_field_names")

        if format in ("json", "csv", "xml"):
            return response
        if format != "df":
            raise ValueError(("Unsupported format: '{}'").format(format))
        if not df_kwargs:
            df_kwargs = {"index_col": "original_field_name"}
        return self.read_csv(StringIO(response), **df_kwargs)

    def export_metadata(self, fields=None, forms=None, format="json", df_kwargs=None):
        """
        Export the project's metadata

        Parameters
        ----------
        fields : list
            Limit exported metadata to these fields
        forms : list
            Limit exported metadata to these forms
        format : (``'json'``), ``'csv'``, ``'xml'``, ``'df'``
            Return the metadata in native objects, csv or xml.
            ``'df'`` will return a ``pandas.DataFrame``.
        df_kwargs : dict
            Passed to ``pandas.read_csv`` to control construction of
            returned DataFrame.
            by default ``{'index_col': 'field_name'}``

        Returns
        -------
        metadata : list, str, ``pandas.DataFrame``
            metadata sttructure for the project.
        """
        ret_format = format
        if format == "df":
            ret_format = "csv"
        payload = self.__basepl("metadata", format=ret_format)
        to_add = [fields, forms]
        str_add = ["fields", "forms"]
        for key, data in zip(str_add, to_add):
            if data:
                for i, value in enumerate(data):
                    payload["{}[{}]".format(key, i)] = value

        response, _ = self._call_api(payload, "metadata")
        if format in ("json", "csv", "xml"):
            return response
        if format != "df":
            raise ValueError(("Unsupported format: '{}'").format(format))

        if not df_kwargs:
            df_kwargs = {"index_col": "field_name"}
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
            for the dateRangeStart filtering of the API
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
        payload = self.__basepl("record", format=ret_format)
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
            fields = fields.extend([name + "_complete" for name in self.forms])

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

    # pylint: disable=import-outside-toplevel
    @staticmethod
    def read_csv(buf, **df_kwargs):
        """Wrapper around pandas read_csv that handles EmptyDataError"""
        from pandas import DataFrame, read_csv
        from pandas.errors import EmptyDataError

        try:
            dataframe = read_csv(buf, **df_kwargs)
        except EmptyDataError:
            dataframe = DataFrame()

        return dataframe

    # pylint: enable=import-outside-toplevel

    def metadata_type(self, field_name):
        """If the given field_name is validated by REDCap, return it's type"""
        return self.__meta_metadata(
            field_name, "text_validation_type_or_show_slider_number"
        )

    def __meta_metadata(self, field, key):
        """Return the value for key for the field in the metadata"""
        metadata_field = ""
        try:
            metadata_field = str(
                [f[key] for f in self.metadata if f["field_name"] == field][0]
            )
        except IndexError:
            print("%s not in metadata field:%s" % (key, field))
            return metadata_field
        else:
            return metadata_field

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

    def names_labels(self, do_print=False):
        """Simple helper function to get all field names and labels """
        if do_print:
            for name, label in zip(self.field_names, self.field_labels):
                print("%s --> %s" % (str(name), str(label)))
        return self.field_names, self.field_labels

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
        payload = self.__basepl("record")
        # pylint: disable=comparison-with-callable
        if hasattr(to_import, "to_csv"):
            # We'll assume it's a df
            buf = StringIO()
            if self.is_longitudinal():
                csv_kwargs = {"index_label": [self.def_field, "redcap_event_name"]}
            else:
                csv_kwargs = {"index_label": self.def_field}
            to_import.to_csv(buf, **csv_kwargs)
            payload["data"] = buf.getvalue()
            buf.close()
            format = "csv"
        elif format == "json":
            payload["data"] = json.dumps(to_import, separators=(",", ":"))
        else:
            # don't do anything to csv/xml
            payload["data"] = to_import
        # pylint: enable=comparison-with-callable
        payload["overwriteBehavior"] = overwrite
        payload["format"] = format
        payload["returnFormat"] = return_format
        payload["returnContent"] = return_content
        payload["dateFormat"] = date_format
        payload["forceAutoNumber"] = force_auto_number
        response = self._call_api(payload, "imp_record")[0]
        if "error" in response:
            raise RedcapError(str(response))
        return response

    def export_file(self, record, field, event=None, return_format="json"):
        """
        Export the contents of a file stored for a particular record

        Notes
        -----
        Unlike other export methods, this works on a single record.

        Parameters
        ----------
        record : str
            record ID
        field : str
            field name containing the file to be exported.
        event: str
            for longitudinal projects, specify the unique event here
        return_format: ('json'), 'csv', 'xml'
            format of error message

        Returns
        -------
        content : bytes
            content of the file
        content_map : dict
            content-type dictionary
        """
        self._check_file_field(field)
        # load up payload
        payload = self.__basepl(content="file", format=return_format)
        # there's no format field in this call
        del payload["format"]
        payload["returnFormat"] = return_format
        payload["action"] = "export"
        payload["field"] = field
        payload["record"] = record
        if event:
            payload["event"] = event
        content, headers = self._call_api(payload, "exp_file")
        # REDCap adds some useful things in content-type
        if "content-type" in headers:
            splat = [
                key_values.strip() for key_values in headers["content-type"].split(";")
            ]
            key_values = [
                (key_values.split("=")[0], key_values.split("=")[1].replace('"', ""))
                for key_values in splat
                if "=" in key_values
            ]
            content_map = dict(key_values)
        else:
            content_map = {}
        return content, content_map

    def import_file(
        self,
        record,
        field,
        fname,
        fobj,
        event=None,
        repeat_instance=None,
        return_format="json",
    ):
        """
        Import the contents of a file represented by fobj to a
        particular records field

        Parameters
        ----------
        record : str
            record ID
        field : str
            field name where the file will go
        fname : str
            file name visible in REDCap UI
        fobj : file object
            file object as returned by `open`
        event : str
            for longitudinal projects, specify the unique event here
        repeat_instance : int
            (only for projects with repeating instruments/events)
            The repeat instance number of the repeating event (if longitudinal)
            or the repeating instrument (if classic or longitudinal).
        return_format : ('json'), 'csv', 'xml'
            format of error message

        Returns
        -------
        response :
            response from server as specified by ``return_format``
        """
        self._check_file_field(field)
        # load up payload
        payload = self.__basepl(content="file", format=return_format)
        # no format in this call
        del payload["format"]
        payload["returnFormat"] = return_format
        payload["action"] = "import"
        payload["field"] = field
        payload["record"] = record
        if event:
            payload["event"] = event
        if repeat_instance:
            payload["repeat_instance"] = repeat_instance
        file_kwargs = {"files": {"file": (fname, fobj)}}
        return self._call_api(payload, "imp_file", **file_kwargs)[0]

    def delete_file(self, record, field, return_format="json", event=None):
        """
        Delete a file from REDCap

        Notes
        -----
        There is no undo button to this.

        Parameters
        ----------
        record : str
            record ID
        field : str
            field name
        return_format : (``'json'``), ``'csv'``, ``'xml'``
            return format for error message
        event : str
            If longitudinal project, event to delete file from

        Returns
        -------
        response : dict, str
            response from REDCap after deleting file
        """
        self._check_file_field(field)
        # Load up payload
        payload = self.__basepl(content="file", format=return_format)
        del payload["format"]
        payload["returnFormat"] = return_format
        payload["action"] = "delete"
        payload["record"] = record
        payload["field"] = field
        if event:
            payload["event"] = event
        return self._call_api(payload, "del_file")[0]

    def _check_file_field(self, field):
        """Check that field exists and is a file field"""
        is_field = field in self.field_names
        is_file = self.__meta_metadata(field, "field_type") == "file"
        if not (is_field and is_file):
            msg = "'%s' is not a field or not a 'file' field" % field
            raise ValueError(msg)

        return True

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
        payload = self.__basepl(content="user", format=format)
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
        payload = self.__basepl(content="participantList", format=format)
        payload["instrument"] = instrument
        if event:
            payload["event"] = event
        return self._call_api(payload, "exp_survey_participant_list")

    def generate_next_record_name(self):
        """Return the next record name for auto-numbering records"""
        payload = self.__basepl(content="generateNextRecordName")

        return self._call_api(payload, "exp_next_id")[0]

    def export_project_info(self, format="json"):
        """
        Export Project Information

        Parameters
        ----------
        format: (json, xml, csv), json by default
            Format of returned data
        """

        payload = self.__basepl(content="project", format=format)

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

        payload = self.__basepl(content="report", format=ret_format)
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
