#!/usr/bin/env python

"""
Copyright (c) 2011, Scott Burns
All rights reserved.
"""

from urllib import urlencode
from urllib2 import Request, urlopen, URLError
import operator as op

from pdb import set_trace

class RCAPIError(Exception):
    pass

class RCRequest(object):
    """Private class wrapping the REDCap API
    
    see https://redcap.vanderbilt.edu/api/help/
    
    Decodes response from redcap and returns it.
    """
    
    def __init__(self, payload, type=''):
        """Constructor
        
        Parameters
        ----------
        payload: dict
            key,values corresponding to the REDCap API
        type: str
            If provided, attempts to validate payload contents against API
        """
        self.url = 'https://redcap.vanderbilt.edu/api/'
        self.payload = payload
        if type:
            self.validate_pl(type)
        self.fmt = payload['format']
            
        # the payload dictionary can have non-url-like objects (specifically,
        # arrays, so let's transfrom payload to a url-like dictionary
        to_encode = {}
        for k,v in payload.iteritems():
            # the only weird thing we might get is an array
            # like exp_record with multiple fields
            # so check if v responds to length and if it's not a string, it's
            # a list we need to unpack in comma-seperated string
            if len(v) > 0 and not isinstance(v, basestring):
                to_encode[str(k)] = ','.join(v)
            else:
                to_encode[str(k)] = str(v)
        self.api_url = urlencode(to_encode)
        
    def validate_pl(self, type):
        """Check that at least required params exist
        
        type: str
            Type of action request
        """
        if type == 'exp_record':
            req = set(('token', 'content', 'format', 'type'))
            if self.payload['content'] != 'record':
                raise RCAPIError('Exporting record but content is not record')
        if type == 'imp_record':
            req = set(('token', 'content', 'format', 'type', 'overwriteBehavior',
                    'data'))
            if self.payload['content'] != 'record':
                raise RCAPIError('Importing record but content is not record')            
        if type == 'metadata':
            req = set(('token', 'content', 'format'))
            if self.payload['content'] != 'metadata':
                raise RCAPIError('Requesting metadata but content is not metadata')
        if type == 'exp_file': 
            req = set(('token', 'content', 'action', 'record', 'field'))
            if self.payload['content'] != 'file':
                raise RCAPIError('Exporting file but content is not file')
        if type == 'imp_file':
            req = set(('token', 'content', 'action', 'record', 'field', 'file'))
            if self.payload['content'] != 'file':
                raise RCAPIError('Importing file but content is not file')
        pl_keys = set(self.payload.keys())
        # if req is not subset of payload keys, this call is wrong
        if not req <= pl_keys:
            #what is not in pl_keys?
            not_pre = req - pl_keys
            raise RCAPIError("Required keys not present: %s" % ', '.join(not_pre))
        
    def execute(self):
        """Execute the API request and return data
        
        Returns:
        response: str
            HTTP reponse code from API
        data: ?
            Depends on format in payload and action
            
        if the RCRequest object was built with payload['format'] == 'json',
        json data structure is returned, otherwise its up to caller to 
        decode.
        """
        request = Request(self.url, self.api_url)
        request.add_header('User-Agent', 'PyCap/0.1 scott.s.burns@vanderbilt.edu')
        response = ''
        try:
            sock = urllib2.urlopen(request)
            response = sock.read()
        except URLError, e:
            if hasattr(e, 'reason'):
                print("Failure to reach RedCap server.")
                print("Reason: %s'" % e.reason)
            if hasattr(e, 'code'):
                print("Server couldn't fulfill request.")
                print("Error code: %s" % e.code)
        else:
            if self.fmt == 'json':
                import json
                try:
                    return json.loads(response)
                except ValueError:
                    print("JSON parsing failed")
            else:
                return response  
        finally:            
            sock.close()

class RCProject(object):
    """Main class representing a RedCap Project"""
    
    def __init__(self, token, name=''):
        """Must init with your token"""
        
        self.token = token
        self.name = name
        
        self.metadata = self.md()
        self.field_names = self.filter_metadata('field_name')
        # we'll use the first field as the default id for each row
        self.def_field = self.field_names[0]
        self.field_labels = self.filter_metadata('field_label')
        
    def md(self):
        """Return the project's metadata structure
        
        Private
        
        """
        
        pl = {'token':self.token, 'content':'metadata',
            'format':'json','type':'flat'}
        metadata = RCRequest(pl, 'metadata').execute()
        return metadata

    def basepl(self, format='json', type='flat'):
        """Return a dictionary which can be used as is or added to for 
        RCRequest payloads"""
        return {'token':self.token, 'format':format, 'type':type}
    
    def filter_metadata(self, key):
        """Return a list values for the key in each field from the project's
        metadata.
        
        Private
        
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
            name has a space in it, replace the space with an underscore (by default, all records are pulled)
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
        pl = self.basepl()
        pl['content'] = 'record'
        keys_to_add = (records, fields, forms, events, rawOrLabel, eventName)
        str_keys = ('records', 'fields', 'forms', 'events', 'rawOrLabel', 
                'eventName')
        for key, data in zip(str_keys, keys_to_add):
            if data:
                pl[key] = data
        return RCRequest(pl, 'exp_record').execute()

    def single_query(self, query):
        """ Pose a single query on the database"""
        # build the fields we need
        fields = [self.def_field, q['f']]
        pl = self.basepl()
        pl['fields'] = fields
        data = RCRequest(pl, 'exp_record').execute()
        

    def compare(self, cmp_str, value1, value2):
        """ """
        cmp_map = {'eq':op.eq, 'ne':op.ne, 'gt':op.gt, 'ge':op.ge, 'le':op.le,
                    'lt':op.lt}
        return cmp_map[cmp_str](value1, value2)

    def query(self, query_list, output_fields=[]):
        """Query the database and return subject information for those
        who match the query logic
        
        Parameters
        ----------
        query_list: list
            list of dicts, which most contain the following keys:
                'f': string of field name to key off of
                'l': 'and' | 'or' 
                'cmp': list of dicts
                    each key is a "verb" from the following:
                        'eq', 'ne', 'le', 'lt', 'ge', 'gt'
                    and value is the value of the comparison
        """
        pass        
