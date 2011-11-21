#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2011, Scott Burns
All rights reserved.
"""

import requests
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
        url: str
            REDCap API URL
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
            try:
                if self.payload['content'] != 'metadata':
                    msg = 'Requesting metadata but content != metadata'
                    raise RCAPIError(msg)
            except KeyError:
                raise RCAPIError('content not in payload')
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
        Return data object from JSON decoding process
        """
        header = {'Content-Type': 'application/x-www-form-urlencoded'}
        r = requests.post(self.url, data=self.payload, headers=header)
        r.raise_for_status()
        return json.loads(r.content)
