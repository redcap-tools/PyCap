#!/usr/bin/env python

"""
Copyright (c) 2011, Scott Burns
All rights reserved.
"""

from urllib import urlencode
from urllib2 import Request, urlopen, URLError


class RCAPIError(Exception):
    pass

class RCRequest(object):
    """Private class wrapping the REDCap API
    
    see https://redcap.vanderbilt.edu/api/help/
    
    Decodes response from redcap and returns it.
    """
    
    def __init__(self, payload={}, type=''):
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
                return json.loads(response)
            else:
                return response  
        finally:            
            sock.close()

