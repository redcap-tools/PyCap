#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2011, Scott Burns
All rights reserved.
"""

import json

from .request import RCRequest


class Project(object):
    """Main class representing a RedCap Project"""

    def __init__(self, url, token, name=''):
        """Must init with your token"""

        self.token = token
        self.name = name
        self.url = url

        self.metadata = self.__md()
        self.field_names = self.filter_metadata('field_name')
        # we'll use the first field as the default id for each row
        self.def_field = self.field_names[0]
        self.field_labels = self.filter_metadata('field_label')
        self.forms = tuple(set(c['form_name'] for c in self.metadata))
        # determine whether longitudinal
        ev_data = RCRequest(self.url, self.__basepl('event'),
            'exp_event').execute()[0]
        if 'error' in ev_data:
            events = tuple([])
            arm_nums = tuple([])
            arm_names = tuple([])
        else:
            events = ev_data
            arm_data = RCRequest(self.url, self.__basepl('arm'),
                'exp_arm').execute()[0]
            arm_nums = tuple([a['arm_num'] for a in arm_data])
            arm_names = tuple([a['name'] for a in arm_data])
        self.events = events
        self.arm_nums = arm_nums
        self.arm_names = arm_names

    def __md(self):
        """Return the project's metadata structure"""
        p_l = self.__basepl('metadata')
        p_l['content'] = 'metadata'
        return RCRequest(self.url, p_l, 'metadata').execute()[0]

    def __basepl(self, content, rec_type='flat', format='json'):
        """Return a dictionary which can be used as is or added to for
        RCRequest payloads"""
        d = {'token': self.token, 'content': content, 'format': format}
        if content not in ['metadata', 'file']:
            d['type'] = rec_type
        return d

    def filter_metadata(self, key):
        """Return a list values for the key in each field from the project's
        metadata.

        Parameters
        ----------
        key: str
            A known key in the metadata structure
        """
        filtered = [field[key] for field in self.metadata if key in field]
        if len(filtered) == 0:
            raise KeyError("Key not found in metadata")
        return filtered

    def export_metadata(self, fields=None, forms=None, format='obj',
            df_kwargs=None):
        """Export the project's metadata

        Parameters
        ----------
        fields: list
            Limit exported metadata to these fields
        forms: list
            Limit exported metadata to these forms
        format: {'obj', 'csv', 'xml', 'df'}, default obj
            Return the metadata in native objects, csv or xml
            df will return a pandas.DataFrame
        df_kwargs: dict [default: {'index_col': 'field_name'}]
            Passed to pandas.read_csv to control construction of
            returned DataFrame
        """
        ret_format = format
        if format == 'obj':
            ret_format = 'json'
        if format == 'df':
            from StringIO import StringIO
            from pandas import read_csv
            ret_format = 'csv'
        pl = self.__basepl('metadata', format=ret_format)
        to_add = [fields, forms]
        str_add = ['fields', 'forms']
        for key, data in zip(str_add, to_add):
            if data:
                pl[key] = ','.join(data)
        response = RCRequest(self.url, pl, 'metadata').execute()[0]
        if format in ('obj', 'csv', 'xml'):
            return response
        elif format == 'df':
            if not df_kwargs:
                df_kwargs = {'index_col': 'field_name'}
            return read_csv(StringIO(response), **df_kwargs)

    def export_records(self, records=None, fields=None, forms=None,
                events=None, raw_or_label='raw', event_name='label',
                format='obj', df_kwargs=None):
        """Return data

        High level function of Project

        Parameters
        ----------
        records: list
            an array of record names specifying specific records you wish to
            pull (by default, all records are pulled)
        fields: list
            an array of field names specifying specific fields you wish to
            pull (by default, all fields are pulled)
        forms: list
            an array of form names you wish to pull records for. If the form
            name has a space in it, replace the space with an underscore
            (by default, all records are pulled)
        events: list
            an array of unique event names that you wish to pull records for -
            only for longitudinal projects
        raw_or_label: 'raw' [default] |  'label' | 'both'
            export the raw coded values or labels for the options of
            multiple choice fields
        event_name: 'label' | 'unique'
             export the unique event name or the event label
        format: 'obj' [default] | 'csv' | 'xml' | 'df'
            Format of returned data. 'obj' returns json-decoded objects
            'csv' and 'xml' return other formats. 'df' will attempt to
            return a pandas.DataFrame.
        df_kwargs: dict [default: {'index_col': self.def_field}]
            Passed to pandas.read_csv to control construction of
            returned DataFrame
        """
        ret_format = format
        if format == 'obj':
            ret_format = 'json'
        if format == 'df':
            from pandas import read_csv
            from StringIO import StringIO
            ret_format = 'csv'
        pl = self.__basepl('record', format=ret_format)
        keys_to_add = (records, fields, forms, events,
                        raw_or_label, event_name)
        str_keys = ('records', 'fields', 'forms', 'events', 'rawOrLabel',
                'eventName')
        for key, data in zip(str_keys, keys_to_add):
            if data:
                #  Make a url-ok string
                if key in ('fields', 'records', 'forms', 'events'):
                    pl[key] = ','.join(data)
                else:
                    pl[key] = data
        response = RCRequest(self.url, pl, 'exp_record').execute()[0]
        if format in ('obj', 'csv', 'xml'):
            return response
        elif format == 'df':
            if not df_kwargs:
                df_kwargs = {'index_col': self.def_field}
            return read_csv(StringIO(response), **df_kwargs)

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
        """ Simple helper function to get all field names and labels """
        if do_print:
            for name, label in zip(self.field_names, self.field_labels):
                print('%s --> %s' % (str(name), str(label)))
        return self.field_names, self.field_labels

    def import_records(self, to_import, overwrite='normal'):
        """ Import data into the RedCap Project

        Parameters
        ----------
        to_import: seq of dicts
            List of dictionaries describing the data you wish to import_records
            Note:
                Keys of the dictionaries should be subset of project's,
                fields, but this isn't a requirement. If you provide keys
                that aren't defined fields, the returned response will
                contain and 'error' key.
        overwrite: 'normal' | 'overwrite'
            'overwrite' will erase values previously stored in the database if
            not specified in the to_import dictionaries
        """
        pl = self.__basepl('record')
        pl['overwriteBehavior'] = overwrite
        pl['data'] = json.dumps(to_import, separators=(',', ':'))
        return RCRequest(self.url, pl, 'imp_record').execute()[0]

    def export_file(self, record, field, event=None, return_format='json'):
        """ Export the contents of a file stored for a particular record

        Note: unlike export_records and import_records, this method
        works on a single record at a time.

        Parameters
        ----------
        record: record ID
        field: field name containing the file to be exported.
        event: for longitudinal projects, specify the unique event here
        return_format: {'json' (default), 'csv', 'xml'}, format of error
            message
        Returns
        -------
        two-tuple of the content of the file and content-type data
        """
        # load up payload
        pl = self.__basepl(content='file', format=return_format)
        # there's no format field in this call
        del pl['format']
        pl['returnFormat'] = return_format
        pl['action'] = 'export'
        if field not in self.field_names:
            raise ValueError("'%s' is not a valid field" % field)
        pl['field'] = field
        pl['record'] = record
        if event:
            pl['event'] = event
        content, headers = RCRequest(self.url, pl, 'exp_file').execute()
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
        """Import the contents of a file represented by fobj to a
        particular records field

        Parameters
        ----------
        record: record ID
        field: field name where the file will go
        fname: file name visible in REDCap UI
        fobj: file object as returned by `open`
        event: for longitudinal projects, specify the unique event here
        return_format: {'json' (default), 'csv', 'xml'}, format of error
            message

        Returns
        -------
        response: response from server as specified by `return_format`
        """
        # load up payload
        pl = self.__basepl(content='file', format=return_format)
        # no format in this call
        del pl['format']
        pl['returnFormat'] = return_format
        pl['action'] = 'import'
        # Check that this is a filed
        if field not in self.field_names:
            raise ValueError("'%s' is not a valid field" % field)
        # Check that it's a 'file' field
        if self.__meta_metadata(field, 'field_type') != 'file':
            raise ValueError("'%s' is not a 'file' field" % field)
        pl['field'] = field
        pl['record'] = record
        if event:
            pl['event'] = event
        file_kwargs = {'files': {'file': (fname, fobj)}}
        return RCRequest(self.url, pl, 'imp_file').execute(**file_kwargs)[0]
    def export_users(self, format='json'):
        """Export the users of the Project

        Each user will have the following keys:
        firstname: User's first name
        lastname: User's last name
        email: Email address
        username: User's username
        expiration: Project access expiration date
        data_access_group: data access group ID
        data_export: (0=no access, 2=De-Identified, 1=Full Data Set)
        forms: a list of dicts with a single key as the form name and
            value is an integer describing that user's form rights,
            where: 0=no access, 1=view records/responses and edit
            records (survey responses are read-only), 2=read only, and
            3=edit survey responses,


        Parameters
        ----------
        format: 'json' (default)|'csv'|'xml', response return format

        Returns
        -------
        list of users dicts when format=json, otherwise a string
        """
        pl = self.__basepl(content='user', format=format)
        return RCRequest(self.url, pl, 'exp_user').execute()[0]
