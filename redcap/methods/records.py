"""REDCap API methods for Project records"""
from io import StringIO

from redcap.request import RedcapError
from redcap.methods.base import Base


class Records(Base):
    """Responsible for all API methods under 'Records' in the API Playground"""

    # pylint: disable=redefined-builtin
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

        for key, data in zip(str_keys, keys_to_add):
            if data:
                if key in ("fields", "records", "forms", "events"):
                    for i, value in enumerate(data):
                        payload[f"{ key }[{ i }]"] = value
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
            raise ValueError(f"Unsupported format: '{ format }'")

        if not df_kwargs:
            if type == "eav":
                df_kwargs = {}
            else:
                if self.is_longitudinal:
                    df_kwargs = {"index_col": [self.def_field, "redcap_event_name"]}
                else:
                    df_kwargs = {"index_col": self.def_field}
        buf = StringIO(response)
        dataframe = self._read_csv(buf, **df_kwargs)
        buf.close()

        return dataframe

    # pylint: enable=too-many-branches
    # pylint: enable=too-many-locals

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
        payload = {}
        payload["action"] = "delete"
        payload["content"] = "record"
        payload["token"] = self.token
        # Turn list of records into dict, and append to payload
        records_dict = {
            f"records[{ idx }]": record for idx, record in enumerate(records)
        }
        payload.update(records_dict)

        payload["format"] = format
        response, _ = self._call_api(payload, "del_record")
        return response

        # pylint: disable=redefined-builtin

    def generate_next_record_name(self):
        """Return the next record name for auto-numbering records"""
        payload = self._basepl(content="generateNextRecordName")

        return self._call_api(payload, "exp_next_id")[0]
