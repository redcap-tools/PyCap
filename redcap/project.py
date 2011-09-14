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

    def __md(self):
        """Return the project's metadata structure"""
        pl = self.__basepl()
        pl['content'] = 'metadata'
        return RCRequest(self.url, pl, 'metadata').execute()

    def __basepl(self, format='json', type='flat'):
        """Return a dictionary which can be used as is or added to for
        RCRequest payloads"""
        return {'token': self.token, 'format': format, 'type': type}

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

    def export_records(self, records=[], fields=[], forms=[], events=[],
                rawOrLabel='raw', eventName='label'):
        """Return data

        Low level function of RCProject

        Parameters
        ----------
        records: list
            an array of record names specifying specific records you wish
            to pull (by default, all records are pulled)
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
        rawOrLabel: 'raw' [default] |  'label' | 'both'
            export the raw coded values or labels for the options of
            multiple choice fields
        eventName: 'label' | 'unique'
             export the unique event name or the event label
        """
        #check that all fields are in self.field_names
        diff = set(fields).difference(set(self.field_names))
        if len(diff) > 0:
            raise ValueError('These fields are not valid: %s' %
                    ' '.join(diff))
        pl = self.__basepl()
        pl['content'] = 'record'
        keys_to_add = (records, fields, forms, events, rawOrLabel, eventName)
        str_keys = ('records', 'fields', 'forms', 'events', 'rawOrLabel',
                'eventName')
        for key, data in zip(str_keys, keys_to_add):
            if data:
                pl[key] = data
        return RCRequest(self.url, pl, 'exp_record').execute()

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

    def filter(self, query, output_fields=[]):
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
        # if output_fields is empty, we'll download all fields, which is
        # not desired
        if not output_fields:
            output_fields = [self.def_field]
        return self.export_records(records=matches, fields=output_fields)

    def names_labels(self, do_print=False):
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
            Keys of the dictionaries must be subset of project's fields
        overwrite: 'normal' | 'overwrite'
            'overwrite' will erase values previously stored in the database if
            not specified in the to_import dictionaries
        """
        all_fields = set(self.field_names)
        passed_fields = [set(d.keys()) for d in to_import]
        is_subsets = map(lambda x: all_fields.issuperset(x), passed_fields)
        if not all(is_subsets):
            msg = "Some fields you passed do not exist in the project"
            raise ValueError(msg)
        pl = self.__basepl()
        pl['overwriteBehavior'] = overwrite
        pl['content'] = 'record'
        pl['data'] = json.dumps(to_import, separators=(',', ':'))
        num_proc = RCRequest(self.url, pl, 'imp_record').execute()
        print("Imported %s records" % num_proc)
