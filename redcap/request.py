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
        fmt_key = 'returnFormat' if 'returnFormat' in payload else 'format'
        self.fmt = payload[fmt_key]

    def validate_pl(self):
        """Check that at least required params exist

        """
        required = ['token', 'content']
        valid_data = {
            'exp_record': (['type', 'format'], 'record',
                'Exporting record but content is not record'),
            'imp_record': (['type', 'overwriteBehavior', 'data', 'format'],
                'record', 'Importing record but content is not record'),
            'metadata': (['format'], 'metadata',
                'Requesting metadata but content != metadata'),
            'exp_file': (['action', 'record', 'field'], 'file',
                'Exporting file but content is not file'),
            'imp_file': (['action', 'record', 'field'], 'file',
                'Importing file but content is not file'),
            'del_file': (['action', 'record', 'field'], 'file',
                'Deleteing file but content is not file'),
            'exp_event': (['format'], 'event',
                'Exporting events but content is not event'),
            'exp_arm': (['format'], 'arm',
                'Exporting arms but content is not arm'),
            'exp_fem': (['format'], 'formEventMapping',
                'Exporting form-event mappings but content != formEventMapping'),
            'exp_user': (['format'], 'user',
                'Exporting users but content is not user')
            }
        extra, req_content, err_msg = valid_data[self.type]
        required.extend(extra)
        required = set(required)
        pl_keys = set(self.payload.keys())
        # if req is not subset of payload keys, this call is wrong
        if not set(required) <= pl_keys:
            #what is not in pl_keys?
            not_pre = required - pl_keys
            raise RCAPIError("Required keys: %s" % ', '.join(not_pre))
        # Check content, raise with err_msg if not good
        try:
            if self.payload['content'] != req_content:
                raise RCAPIError(err_msg)
        except KeyError:
            raise RCAPIError('content not in payload')

    def execute(self, **kwargs):
        """Execute the API request and return data

        Parameters
        ----------
        kwargs: passed to requests.post()

        Returns
        -------
        Return data object from JSON decoding process if format=='json',
        else return raw string (ie format=='csv'|'xml')
        """
        r = requests.post(self.url, data=self.payload, **kwargs)
        # Raise if we need to
        self.raise_for_status(r)
        content = self.get_content(r)
        return content, r.headers

    def get_content(self, r):
        """Abstraction for grabbing content from a returned response"""
        if self.type == 'exp_file':
            # don't use the decoded r.text
            return r.content
        else:
            if self.fmt == 'json':
                content = {}
                # Decode
                try:
                    # Watch out for bad/empty json
                    content = json.loads(r.text, strict=False)
                except ValueError as e:
                    if not self.expect_empty_json():
                        # reraise for requests that shouldn't send empty json
                        raise ValueError(e)
                finally:
                    return content
            else:
                return r.text

    def expect_empty_json(self):
        """Some responses are known to send empty responses"""
        return self.type in ('imp_file', 'del_file')

    def raise_for_status(self, r):
        """Given a response, raise for bad status for certain actions

        Some redcap api methods don't return error messages
        that the user could test for or otherwise use. Therefore, we
        need to do the testing ourself

        Raising for everything wouldn't let the user see the
        (hopefully helpful) error  message"""
        if self.type in ('exp_file', 'imp_file', 'del_file'):
            r.raise_for_status()
