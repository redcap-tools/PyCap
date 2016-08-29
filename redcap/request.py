#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Scott Burns <scott.s.burns@vanderbilt.edu>'
__license__ = 'MIT'
__copyright__ = '2014, Vanderbilt University'

"""

Low-level HTTP functionality

"""

__author__ = 'Scott Burns'
__copyright__ = ' Copyright 2014, Vanderbilt University'


from requests import post, RequestException
import json


RedcapError = RequestException


class RCAPIError(Exception):
    """ Errors corresponding to a misuse of the REDCap API """
    pass


class RCRequest(object):
    """
    Private class wrapping the REDCap API. Decodes response from redcap
    and returns it.

    References
    ----------
    https://redcap.vanderbilt.edu/api/help/

    Users shouldn't really need to use this, the Project class is the
    biggest consumer.
    """

    def __init__(self, url, payload, qtype):
        """
        Constructor

        Parameters
        ----------
        url : str
            REDCap API URL
        payload : dict
            key,values corresponding to the REDCap API
        qtype : str
            Used to validate payload contents against API
        """
        self.url = url
        self.payload = payload
        self.type = qtype
        if qtype:
            self.validate()
        fmt_key = 'returnFormat' if 'returnFormat' in payload else 'format'
        self.fmt = payload[fmt_key]

    def validate(self):
        """Checks that at least required params exist"""
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
                'Exporting users but content is not user'),
	        'version': (['format'], 'version',
                'Requesting version but content != version'),
            'exp_project': (['format'], 'project',
                'Requesting project info but content is not project'),
            'exp_report': (['report_id', 'format'], 'report',
                'Exporting report but content is not report'),
            'exp_instrument': (['format'], 'instrument',
                'Exporting instruments but content is not instrument'),
            'exp_pdf': (['format'], 'pdf',
                'Exporting pdf but content is not pdf'),
            'exp_surveyLink': (['record', 'instrument', 'event'], 'surveyLink',
                'Exporting survey link but content is not surveyLink'),
            'exp_surveyQueueLink': (['record'], 'surveyQueueLink',
                'Exporting survey queue link but content is not surveyQueueLink'),
            'exp_surveyReturnCode': (['instrument', 'event'], 'surveyReturnCode',
                'Exporting survey return code but content is not surveyReturnCode'),
            'exp_participantList': (['instrument', 'event', 'format'], 'participantList',
                'Exporting survey participant list but content is not participantList'),
            'exp_exportFieldNames': (['format'], 'exportFieldNames',
                'Exporting field names but content is not exportFieldNames'),
            'imp_arm': (['override', 'action', 'format', 'data'], 'arm',
                'Importing arms but content is not arm'),
            'imp_event': (['action', 'override', 'format', 'data'], 'event',
                'Importing events but content is not event'),
            'imp_fem': (['format', 'data'], 'formEventMapping',
                'Importing instrument, form-event mapping but conent is not formEventMapping'),
            'imp_metadata': (['format', 'data'], 'metadata',
                'Importing metadata but content is not metadata'),
            'imp_users': (['format', 'data'], 'user',
                'Importing users but conent is not user'),
            'del_arm': (['action', 'arms'], 'arm',
                'Deleting arms but content is not arm'),
            'del_event': (['action', 'events'], 'event',
                'Deleting events but content is not event'),
            'create_project': (['format', 'data'], 'project',
                'Creating new project but content is not project')
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
        kwargs :
            passed to requests.post()

        Returns
        -------
        response : list, str
            data object from JSON decoding process if format=='json',
            else return raw string (ie format=='csv'|'xml')
        """
        r = post(self.url, data=self.payload, **kwargs)
        # Raise if we need to
        self.raise_for_status(r)
        content = self.get_content(r)
        return content, r.headers

    def get_content(self, r):
        """Abstraction for grabbing content from a returned response"""
        if self.type == 'exp_file':
            # don't use the decoded r.text
            return r.content
        elif self.type == 'version':
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
        (hopefully helpful) error message"""
        if self.type in ('metadata', 'exp_file', 'imp_file', 'del_file'):
            r.raise_for_status()
        # see http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
        # specifically 10.5
        if 500 <= r.status_code < 600:
            raise RedcapError(r.content)
