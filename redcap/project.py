#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Scott Burns <scott.s.burns@vanderbilt.edu>'
__license__ = 'MIT'
__copyright__ = '2014, Vanderbilt University'

import json
import warnings

from .request import RCRequest, RedcapError, RequestException
import semantic_version

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

try:
    from pandas import read_csv
except ImportError:
    read_csv = None


class Project(object):
    """Main class for interacting with REDCap projects"""

    def __init__(self, url, token, name='', verify_ssl=True, lazy=False):
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
        # Add more detailed project info
        #   Stored in dictionary to safe space and clarity
        self.project_info = None

        if not lazy:
            self.configure()

    def configure(self):
        try:
            self.metadata = self.__md()
        except RequestException:
            raise RedcapError("Exporting metadata failed. Check your URL and token.")
        try:
            self.redcap_version = self.__rcv()
        except:
            raise RedcapError("Determination of REDCap version failed")
        try:
            self.project_info = self.export_project()
        except RequestException:
            raise RedcapError("Exporting project information failed")

        self.field_names = self.filter_metadata('field_name')
        # we'll use the first field as the default id for each row
        self.def_field = self.field_names[0]
        self.field_labels = self.filter_metadata('field_label')
        self.forms = tuple(set(c['form_name'] for c in self.metadata))
        # determine whether longitudinal
        ev_data = self._call_api(self.__basepl('event'), 'exp_event')[0]
        arm_data = self._call_api(self.__basepl('arm'), 'exp_arm')[0]

        if isinstance(ev_data, dict) and ('error' in ev_data.keys()):
            events = tuple([])
        else:
            events = ev_data
            
        if isinstance(arm_data, dict) and ('error' in arm_data.keys()):
            arm_nums = tuple([])
            arm_names = tuple([])
        else:
            arm_nums = tuple([a['arm_num'] for a in arm_data])
            arm_names = tuple([a['name'] for a in arm_data])
        self.events = events
        self.arm_nums = arm_nums
        self.arm_names = arm_names
        self.configured = True

    def __md(self):
        """Return the project's metadata structure"""
        p_l = self.__basepl('metadata')
        p_l['content'] = 'metadata'
        return self._call_api(p_l, 'metadata')[0]

    def __basepl(self, content, rec_type='flat', format='json'):
        """Return a dictionary which can be used as is or added to for
        payloads"""
        d = {'token': self.token, 'content': content, 'format': format}
        if content not in ['metadata', 'file']:
            d['type'] = rec_type
        return d

    def __rcv(self):
        p_l = self.__basepl('version')
        rcv = self._call_api(p_l, 'version')[0].decode('utf-8')
        if 'error' in rcv:
            warnings.warn('Version information not available for this REDCap instance')
            return ''
        if semantic_version.validate(rcv):
            return semantic_version.Version(rcv)
        else:
            return rcv

    def is_longitudinal(self):
        """
        Returns
        -------
        boolean :
            longitudinal status of this project
        """
        return len(self.events) > 0 and \
            len(self.arm_nums) > 0 and \
            len(self.arm_names) > 0

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
        return {'verify': self.verify}

    def _call_api(self, payload, typpe, **kwargs):
        request_kwargs = self._kwargs()
        request_kwargs.update(kwargs)
        rcr = RCRequest(self.url, payload, typpe)
        return rcr.execute(**request_kwargs)

    def export_project(self, format='json',df_kwargs=None):
        """
        Export the project's information (REDCap >= 6.5.0)

        Parameters
        ----------
        format : (``'json'``), ``'csv'``, ``'xml'``
            Return the project information,
            csv or xml, ``'df''`` will return a ``pandas.DataFrame``
        df_kwargs : dict
            Passed to pandas.read_csv to control construction of
            returned DataFrame

        Returns
        -------
        project: list, str, ``pandas.DataFrame``
            project information
        """

        # Check for dataframe usage
        if not read_csv and format == 'df':
            warnings.warn('Pandas csv_reader not available, dataframe replaced with csv format')
            format = 'csv'

        pl = self.__basepl('project')
        response, _ = self._call_api(pl, 'exp_project')

        if format in ('json', 'csv', 'xml'):
            return response
        elif format == 'df':
            if not df_kwargs:
                return read_csv(StringIO(response))
            else:
                return read_csv(StringIO(response), **df_kwargs)   

    def export_report(self, report_id, format='json', raw_or_label='raw', raw_or_label_headers='raw', export_checkbox_labels=False, df_kwargs=None):
        """
        Export the project's report (REDCap >= 6.0.0)

        Parameters
        ----------
        format : (``'json'``), ``'csv'``, ``'xml'``
            Return the project report data,
            csv or xml, ``'df''`` will return a ``pandas.DataFrame``
        report_id: str
            report ID
        raw_or_label : (``'raw'``), ``'label'``,
            export the raw coded values or labels for the options of
            multiple choice fields, or both
        raw_or_label_headers: (``'raw'``), ``'label'``
            For "csv" & "flat" type only, exports variable/field names (raw)
            or the field labels (label)
        export_checkbox_labels : (``False``), ``True``
            specify whether to export checkbox values as their label on
            export.
        df_kwargs : dict
            Passed to pandas.read_csv to control construction of
            returned DataFrame

        Returns
        -------
        report: list, str, ``pandas.DataFrame``
            report data from project
        """

        # Check for dataframe usage
        if not read_csv and format == 'df':
            warnings.warn('Pandas csv_reader not available, dataframe replaced with csv format')
            format = 'csv'

        pl = self.__basepl('report')

        to_add = (report_id, raw_or_label, raw_or_label_headers, export_checkbox_labels)
        str_add = ('report_id', 'rawOrLabel', 'rawOrLabelHeadHeaders', 'exportCheckboxLabel')
        for key, data in zip(str_add, to_add):
            if data:
                pl[key] = data

        response, _ = self._call_api(pl, 'exp_report')        

        if format in ('json', 'csv', 'xml'):
            return response
        elif format == 'df':
            if not df_kwargs:
                return read_csv(StringIO(response))
            else:
                return read_csv(StringIO(response), **df_kwargs)  

    def export_instruments(self, format='json', df_kwargs=None):
        """
        Export the project's instruments

        Parameters
        ----------
        format : (``'json'``), ``'csv'``, ``'xml'``
            Return the list of project instruments in native objects,
            csv or xml, ``'df''`` will return a ``pandas.DataFrame``
        df_kwargs : dict
            Passed to pandas.read_csv to control construction of
            returned DataFrame

        Returns
        -------
        instruments: list, str, ``pandas.DataFrame``
            list of data collection instruments
        """

        # Check for dataframe usage
        if not read_csv and format == 'df':
            warnings.warn('Pandas csv_reader not available, dataframe replaced with csv format')
            format = 'csv'

        pl = self.__basepl('instrument')
        response, _ = self._call_api(pl, 'exp_instrument')

        if format in ('json', 'csv', 'xml'):
            return response
        elif format == 'df':
            if not df_kwargs:
                return read_csv(StringIO(response))
            else:
                return read_csv(StringIO(response), **df_kwargs)   

    def export_pdf(self, format='json', record=None, event=None, instrument=None, all_records=None, df_kwargs=None):
        """
        Export the project's instrument data as pdf (REDCap >= 6.4.0)

        Parameters
        ----------
        format : (``'json'``), ``'csv'``, ``'xml'``
            format of error message,
            csv or xml, ``'df''`` will return a ``pandas.DataFrame``
        record: str
            record ID, if left blank will return blank PDF
        event: str
            event name, for longitudinal projects only, if blank when
            record is supplied, will return all events for that record
        instrument: str
            instrument name, if blank, returns all instruments
        all_records: str
            value does not matter, if parameter is passed with any value,
            all instruments and all records will be exported
        df_kwargs : dict
            Passed to pandas.read_csv to control construction of
            returned DataFrame

        Returns
        -------
        content : bytes
            content of the file
        content_map : dict
            content-type dictionary
        """

        # Check for dataframe usage
        if not read_csv and format == 'df':
            warnings.warn('Pandas csv_reader not available, dataframe replaced with csv format')
            format = 'csv'

        pl = self.__basepl('pdf')

        to_add = (record, event, instrument, all_records)
        str_add = ("record", "event", "instrument", "allrecords")
        for key, data in zip(str_add, to_add):
            if data:
                pl[key] = data

        content, headers = self._call_api(pl, 'exp_pdf')      

        # NOTE: reusing methodology from 'export_file"'
        #REDCap adds some useful things in content-type
        if 'content-type' in headers:
            splat = [kv.strip() for kv in headers['content-type'].split(';')]
            kv = [(kv.split('=')[0], kv.split('=')[1].replace('"', '')) for kv
                  in splat if '=' in kv]
            content_map = dict(kv)
        else:
            content_map = {}
        return content, content_map

    def export_survey_link(self, record, instrument, event=None, format='json'):
        """
        Export unique survey link for specific record and instrument (REDCap >= 6.4.0)

        Parameters
        ----------
        format : (``'json'``), ``'csv'``, ``'xml'``
            format of error message,
            csv or xml, ``'df''`` will return a ``pandas.DataFrame``
        record: str
            record ID
        instrument: str
            instrument name
        event: str
            event name (for longitudinal projects only)
        df_kwargs : dict
            Passed to pandas.read_csv to control construction of
            returned DataFrame

        Returns
        -------
        survey_link: list, str, ``pandas.DataFrame``
            unique survey link
        """

        # Check for dataframe usage
        if not read_csv and format == 'df':
            warnings.warn('Pandas csv_reader not available, dataframe replaced with csv format')
            format = 'csv'

        pl = self.__basepl('surveyLink')

        # Require event if project is longitudinal
        if self.is_longitudinal() == True and event is None:
            print("Error: 'event' is required for longitudinal projects")
            return
        else:  
            event = "filler"

        to_add = (record, instrument, event)
        str_add = ("record", "instrument", "event")
        for key, data in zip(str_add, to_add):
            if data:
                pl[key] = data

        response, _ = self._call_api(pl, 'exp_surveyLink')

        if format in ('json', 'csv', 'xml'):
            return response
        elif format == 'df':
            if not df_kwargs:
                return read_csv(StringIO(response))
            else:
                return read_csv(StringIO(response), **df_kwargs)   

    def export_survey_queue_link(self, record, format='json'):
        """
        Export unique survey queue link for specific record  (REDCap >= 6.4.0)

        Parameters
        ----------
        format : (``'json'``), ``'csv'``, ``'xml'``
            format of error message,
            csv or xml, ``'df''`` will return a ``pandas.DataFrame``
        record: str
            record ID
            event name (for longitudinal projects only)
        df_kwargs : dict
            Passed to pandas.read_csv to control construction of
            returned DataFrame

        Returns
        -------
        survey_link: list, str, ``pandas.DataFrame``
            unique survey queue link
        """

        # Check for dataframe usage
        if not read_csv and format == 'df':
            warnings.warn('Pandas csv_reader not available, dataframe replaced with csv format')
            format = 'csv'

        pl = self.__basepl('surveyQueueLink')

        pl["record"] = record

        response, _ = self._call_api(pl, 'exp_surveyQueueLink')

        if format in ('json', 'csv', 'xml'):
            return response
        elif format == 'df':
            if not df_kwargs:
                return read_csv(StringIO(response))
            else:
                return read_csv(StringIO(response), **df_kwargs)   

    def export_survey_return_code(self, record, instrument, event=None, format='json'):
        """
        Export survey return code for specific record and instrument  (REDCap >= 6.4.0)

        Parameters
        ----------
        format : (``'json'``), ``'csv'``, ``'xml'``
            format of error message,
            csv or xml, ``'df''`` will return a ``pandas.DataFrame``
        record: str
            record ID
        instrument: str
            instrument name
        event: str
            event name (for longitudinal projects only)
        df_kwargs : dict
            Passed to pandas.read_csv to control construction of
            returned DataFrame

        Returns
        -------
        survey_link: list, str, ``pandas.DataFrame``
            unique survey return code
        """

        # Check for dataframe usage
        if not read_csv and format == 'df':
            warnings.warn('Pandas csv_reader not available, dataframe replaced with csv format')
            format = 'csv'

        pl = self.__basepl('surveyReturnCode')

        # Require event if project is longitudinal
        if self.is_longitudinal() == True and event is None:
            print("Error: 'event' is required for longitudinal projects")
            return
        else:  
            event = "filler"

        to_add = (record, instrument, event)
        str_add = ("record", "instrument", "event")
        for key, data in zip(str_add, to_add):
            if data:
                pl[key] = data

        response, _ = self._call_api(pl, 'exp_surveyReturnCode')

        if format in ('json', 'csv', 'xml'):
            return response
        elif format == 'df':
            if not df_kwargs:
                return read_csv(StringIO(response))
            else:
                return read_csv(StringIO(response), **df_kwargs)   

    def export_participant_list(self, instrument, event=None, format='json', df_kwargs=None):
        """
        Export survey participant list for specific instrument  (REDCap >= 6.4.0)

        Parameters
        ----------
        format : (``'json'``), ``'csv'``, ``'xml'``
            format of error message,
            csv or xml, ``'df''`` will return a ``pandas.DataFrame``
        instrument: str
            instrument name
        event: str
            event name (for longitudinal projects only)
        df_kwargs : dict
            Passed to pandas.read_csv to control construction of
            returned DataFrame

        Returns
        -------
        survey_link: list, str, ``pandas.DataFrame``
            survey participant list for specific instrument
        """

        # Check for dataframe usage
        if not read_csv and format == 'df':
            warnings.warn('Pandas csv_reader not available, dataframe replaced with csv format')
            format = 'csv'

        pl = self.__basepl('participantList')

        # Require event if project is longitudinal
        if self.is_longitudinal() == True and event is None:
            print("Error: 'event' is required for longitudinal projects")
            return
        else:  
            event = "filler"

        to_add = (instrument, event)
        str_add = ("instrument", "event")
        for key, data in zip(str_add, to_add):
            if data:
                pl[key] = data

        response, _ = self._call_api(pl, 'exp_participantList')

        if format in ('json', 'csv', 'xml'):
            return response
        elif format == 'df':
            if not df_kwargs:
                return read_csv(StringIO(response))
            else:
                return read_csv(StringIO(response), **df_kwargs) 

    def export_fieldnames(self, format='json', field=None, df_kwargs=None):
        """
        Export list of import/export-specific field names  (REDCap >= 6.4.0)

        Parameters
        ----------
        format : (``'json'``), ``'csv'``, ``'xml'``
            Return the list of project instruments in native objects,
            csv or xml, ``'df''`` will return a ``pandas.DataFrame``
        df_kwargs : dict
            Passed to pandas.read_csv to control construction of
            returned DataFrame

        Returns
        -------
        instruments: list, str, ``pandas.DataFrame``
            list of field names
        """
        
        # Check for dataframe usage
        if not read_csv and format == 'df':
            warnings.warn('Pandas csv_reader not available, dataframe replaced with csv format')
            format = 'csv'

        pl = self.__basepl('exportFieldNames')
        pl["field"] = field
        
        response, _ = self._call_api(pl, 'exp_exportFieldNames')

        if format in ('json', 'csv', 'xml'):
            return response
        elif format == 'df':
            if not df_kwargs:
                return read_csv(StringIO(response))
            else:
                return read_csv(StringIO(response), **df_kwargs)   

    def export_fem(self, arms=None, format='json', df_kwargs=None):
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
        
        # Check for dataframe usage
        if not read_csv and format == 'df':
            warnings.warn('Pandas csv_reader not available, dataframe replaced with csv format')
            format = 'csv'

        pl = self.__basepl('formEventMapping', format=format)
        to_add = [arms]
        str_add = ['arms']
        for key, data in zip(str_add, to_add):
            if data:
                pl[key] = ','.join(data)
        response, _ = self._call_api(pl, 'exp_fem')
        if format in ('json', 'csv', 'xml'):
            return response
        elif format == 'df':
            if not df_kwargs:
                return read_csv(StringIO(response))
            else:
                return read_csv(StringIO(response), **df_kwargs)

    def export_metadata(self, fields=None, forms=None, format='json',
            df_kwargs=None):
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
        # Check for dataframe usage
        if not read_csv and format == 'df':
            warnings.warn('Pandas csv_reader not available, dataframe replaced with csv format')
            format = 'csv'

        pl = self.__basepl('metadata', format=format)
        to_add = [fields, forms]
        str_add = ['fields', 'forms']
        for key, data in zip(str_add, to_add):
            if data:
                pl[key] = ','.join(data)
        response, _ = self._call_api(pl, 'metadata')
        if format in ('json', 'csv', 'xml'):
            return response
        elif format == 'df':
            if not df_kwargs:
                df_kwargs = {'index_col': 'field_name'}
            return read_csv(StringIO(response), **df_kwargs)

    def export_records(self, records=None, fields=None, forms=None,
    events=None, raw_or_label='raw', event_name='label',
    format='json', export_survey_fields=False,
    export_data_access_groups=False, df_kwargs=None,
    export_checkbox_labels=False):
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

        Returns
        -------
        data : list, str, ``pandas.DataFrame``
            exported data
        """
        # Check for dataframe usage
        if not read_csv and format == 'df':
            warnings.warn('Pandas csv_reader not available, dataframe replaced with csv format')
            format = 'csv'

        pl = self.__basepl('record', format=format)
        fields = self.backfill_fields(fields, forms)
        keys_to_add = (records, fields, forms, events,
        raw_or_label, event_name, export_survey_fields,
        export_data_access_groups, export_checkbox_labels)
        str_keys = ('records', 'fields', 'forms', 'events', 'rawOrLabel',
        'eventName', 'exportSurveyFields', 'exportDataAccessGroups',
        'exportCheckboxLabel')
        for key, data in zip(str_keys, keys_to_add):
            if data:
                #  Make a url-ok string
                if key in ('fields', 'records', 'forms', 'events'):
                    pl[key] = ','.join(data)
                else:
                    pl[key] = data
        response, _ = self._call_api(pl, 'exp_record')
        if format in ('json', 'csv', 'xml'):
            return response
        elif format == 'df':
            if not df_kwargs:
                if self.is_longitudinal():
                    df_kwargs = {'index_col': [self.def_field,
                                               'redcap_event_name']}
                else:
                    df_kwargs = {'index_col': self.def_field}
            buf = StringIO(response)
            df = read_csv(buf, **df_kwargs)
            buf.close()
            return df

    def metadata_type(self, field_name):
        """If the given field_name is validated by REDCap, return it's type"""
        return self.__meta_metadata(field_name,
                                    'text_validation_type_or_show_slider_number')

    def __meta_metadata(self, field, key):
        """Return the value for key for the field in the metadata"""
        mf = ''
        try:
            mf = str([f[key] for f in self.metadata
                     if f['field_name'] == field][0])
        except IndexError:
            print("%s not in metadata field:%s" % (key, field))
            return mf
        else:
            return mf

    def backfill_fields(self, fields, forms):
        """ Properly backfill fields to explicitly request specific
        keys. The issue is that >6.X servers *only* return requested fields
        so to improve backwards compatiblity for PyCap clients, add specific fields
        when required.

        Parameters
        ----------
            fields: list
                requested fields
            forms: list
                requested forms
        Returns:
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

    def filter(self, query, output_fields=None):
        """Query the database and return subject information for those
        who match the query logic

        Parameters
        ----------
        query: Query or QueryGroup
            Query(Group) object to process
        output_fields: list
            The fields desired for matching subjects

        Returns
        -------
        A list of dictionaries whose keys contains at least the default field
        and at most each key passed in with output_fields, each dictionary
        representing a surviving row in the database.
        """
        query_keys = query.fields()
        if not set(query_keys).issubset(set(self.field_names)):
            raise ValueError("One or more query keys not in project keys")
        query_keys.append(self.def_field)
        data = self.export_records(fields=query_keys)
        matches = query.filter(data, self.def_field)
        if matches:
            # if output_fields is empty, we'll download all fields, which is
            # not desired, so we limit download to def_field
            if not output_fields:
                output_fields = [self.def_field]
            #  But if caller passed a string and not list, we need to listify
            if isinstance(output_fields, basestring):
                output_fields = [output_fields]
            return self.export_records(records=matches, fields=output_fields)
        else:
            #  If there are no matches, then sending an empty list to
            #  export_records will actually return all rows, which is not
            #  what we want
            return []

    def names_labels(self, do_print=False):
        """Simple helper function to get all field names and labels """
        if do_print:
            for name, label in zip(self.field_names, self.field_labels):
                print('%s --> %s' % (str(name), str(label)))
        return self.field_names, self.field_labels

    def import_records(self, to_import, overwrite='normal', format='json',
        return_format='json', return_content='count',
            date_format='YMD'):
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

        Returns
        -------
        response : dict, str
            response from REDCap API, json-decoded if ``return_format`` == ``'json'``
        """
        pl = self.__basepl('record')
        if hasattr(to_import, 'to_csv'):
            # We'll assume it's a df
            from StringIO import StringIO
            buf = StringIO()
            if self.is_longitudinal():
                csv_kwargs = {'index_label': [self.def_field,
                                              'redcap_event_name']}
            else:
                csv_kwargs = {'index_label': self.def_field}
            to_import.to_csv(buf, **csv_kwargs)
            pl['data'] = buf.getvalue()
            buf.close()
            format = 'csv'
        elif format == 'json':
            pl['data'] = json.dumps(to_import, separators=(',', ':'))
        else:
            # don't do anything to csv/xml
            pl['data'] = to_import
        pl['overwriteBehavior'] = overwrite
        pl['format'] = format
        pl['returnFormat'] = return_format
        pl['returnContent'] = return_content
        pl['dateFormat'] = date_format
        response = self._call_api(pl, 'imp_record')[0]
        if 'error' in response:
            raise RedcapError(str(response))
        return response

    def export_file(self, record, field, event=None, return_format='json'):
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
        pl = self.__basepl(content='file', format=return_format)
        # there's no format field in this call
        del pl['format']
        pl['returnFormat'] = return_format
        pl['action'] = 'export'
        pl['field'] = field
        pl['record'] = record
        if event:
            pl['event'] = event
        content, headers = self._call_api(pl, 'exp_file')
        #REDCap adds some useful things in content-type
        if 'content-type' in headers:
            splat = [kv.strip() for kv in headers['content-type'].split(';')]
            kv = [(kv.split('=')[0], kv.split('=')[1].replace('"', '')) for kv
                  in splat if '=' in kv]
            content_map = dict(kv)
        else:
            content_map = {}
        return content, content_map

    def import_file(self, record, field, fname, fobj, event=None,
            return_format='json'):
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
        return_format : ('json'), 'csv', 'xml'
            format of error message

        Returns
        -------
        response :
            response from server as specified by ``return_format``
        """
        self._check_file_field(field)
        # load up payload
        pl = self.__basepl(content='file', format=return_format)
        # no format in this call
        del pl['format']
        pl['returnFormat'] = return_format
        pl['action'] = 'import'
        pl['field'] = field
        pl['record'] = record
        if event:
            pl['event'] = event
        file_kwargs = {'files': {'file': (fname, fobj)}}
        return self._call_api(pl, 'imp_file', **file_kwargs)[0]

    def delete_file(self, record, field, return_format='json', event=None):
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
        pl = self.__basepl(content='file', format=return_format)
        del pl['format']
        pl['returnFormat'] = return_format
        pl['action'] = 'delete'
        pl['record'] = record
        pl['field'] = field
        if event:
            pl['event'] = event
        return self._call_api(pl, 'del_file')[0]

    def _check_file_field(self, field):
        """Check that field exists and is a file field"""
        is_field = field in self.field_names
        is_file = self.__meta_metadata(field, 'field_type') == 'file'
        if not (is_field and is_file):
            msg = "'%s' is not a field or not a 'file' field" % field
            raise ValueError(msg)
        else:
            return True

    def export_users(self, format='json'):
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
        pl = self.__basepl(content='user', format=format)
        return self._call_api(pl, 'exp_user')[0]
