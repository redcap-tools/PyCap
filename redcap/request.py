#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2011, Scott Burns
All rights reserved.
"""

from urllib import urlencode
from urllib2 import Request, urlopen, URLError
import json


class RCAPIError(Exception):
    """ Errors corresponding to a misuse of the REDCap API """
    pass


class RCRequest(object):
    """Private class wrapping the REDCap API

    see https://redcap.vanderbilt.edu/api/help/

    Decodes response from redcap and returns it.

    Users shouldn't really need to use this, the Project class will use this.
    """

    def __init__(self, url, payload, qtype):
        """Constructor

        Parameters
        ----------
        payload: dict
            key,values corresponding to the REDCap API
        qtype: 'imp_record' | 'exp_record' | 'metadata'
            Used to validate payload contents against API
        """
        self.url = url
        self.payload = payload
        self.type = qtype
        if qtype:
            self.validate_pl()
        self.fmt = payload['format']

        # the payload dictionary can have non-url-like objects (specifically,
        # arrays, so let's transfrom payload to a url-like dictionary
        to_encode = {}
        for k, v in payload.iteritems():
            # the only weird thing we might get is an array
            # like exp_record with multiple fields
            # so check if v responds to length and if it's not a string, it's
            # a list we need to unpack in comma-seperated string
            if len(v) > 0 and not isinstance(v, basestring):
                to_encode[str(k)] = ','.join(v)
            else:
                to_encode[str(k)] = str(v)
        self.api_url = urlencode(to_encode)

    def validate_pl(self):
        """Check that at least required params exist

        """
        if self.type == 'exp_record':
            req = set(('token', 'content', 'format', 'type'))
            if self.payload['content'] != 'record':
                raise RCAPIError('Exporting record but content is not record')
        if self.type == 'imp_record':
            req = set(('token', 'content', 'format', 'type',
                        'overwriteBehavior', 'data'))
            if self.payload['content'] != 'record':
                raise RCAPIError('Importing record but content is not record')
        if self.type == 'metadata':
            req = set(('token', 'content', 'format'))
            if self.payload['content'] != 'metadata':
                raise RCAPIError('Requesting metadata but content != metadata')
        if self.type == 'exp_file':
            req = set(('token', 'content', 'action', 'record', 'field'))
            if self.payload['content'] != 'file':
                raise RCAPIError('Exporting file but content is not file')
        if self.type == 'imp_file':
            req = set(('token', 'content', 'action', 'record',
                        'field', 'file'))
            if self.payload['content'] != 'file':
                raise RCAPIError('Importing file but content is not file')
        pl_keys = set(self.payload.keys())
        # if req is not subset of payload keys, this call is wrong
        if not req <= pl_keys:
            #what is not in pl_keys?
            not_pre = req - pl_keys
            raise RCAPIError("Required keys: %s" % ', '.join(not_pre))

    def execute(self):
        """Execute the API request and return data

        Returns
        -------
        data: ?
            Depends on format in payload and action

        if the RCRequest object was built with payload['format'] == 'json',
        json data structure is returned, otherwise its up to caller to
        decode.
        """
        request = Request(self.url, self.api_url)
        request.add_header('User-Agent', 'PyCap')
        if 'imp' in self.type:
            request.add_header('Content-Type',
                                'application/x-www-form-urlencoded')
        response = ''
        try:
            response = urlopen(request)
        except URLError, e:
            if hasattr(e, 'reason'):
                print("Failure to reach RedCap server.")
                print("Reason: %s'" % e.reason)
            if hasattr(e, 'code'):
                print("Server couldn't fulfill request.")
                print("Error code: %s" % e.code)
            error_text = e.read()
            if error_text:
                print("Response from server: %s" % error_text)
        else:
            resp_str = response.read()
            response.close()
            to_return = resp_str
            if self.fmt == 'json':
                try:
                    to_return = json.loads(resp_str)
                except ValueError:
                    print("JSON parsing failed")
            return to_return
