#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Low-level HTTP functionality

"""

import json
from requests import RequestException, Session

__author__ = "Scott Burns <scott.s.burns@gmail.com>"
__license__ = "MIT"
__copyright__ = "2014, Vanderbilt University"

RedcapError = RequestException

_session = Session()


class RCAPIError(Exception):
    """ Errors corresponding to a misuse of the REDCap API """


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

    def __init__(self, url, payload, qtype, session=_session):
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
        self.session = session

        if qtype:
            self.validate()
        fmt_key = "returnFormat" if "returnFormat" in payload else "format"
        self.fmt = payload[fmt_key]

    def validate(self):
        """Checks that at least required params exist"""
        required = ["token", "content"]
        valid_data = {
            "exp_record": (
                ["type", "format"],
                "record",
                "Exporting record but content is not record",
            ),
            "exp_field_names": (
                ["format"],
                "exportFieldNames",
                "Exporting field names, but content is not exportFieldNames",
            ),
            "del_record": (
                ["format"],
                "record",
                "Deleting record but content is not record",
            ),
            "imp_record": (
                ["type", "overwriteBehavior", "data", "format"],
                "record",
                "Importing record but content is not record",
            ),
            "metadata": (
                ["format"],
                "metadata",
                "Requesting metadata but content != metadata",
            ),
            "exp_file": (
                ["action", "record", "field"],
                "file",
                "Exporting file but content is not file",
            ),
            "imp_file": (
                ["action", "record", "field"],
                "file",
                "Importing file but content is not file",
            ),
            "del_file": (
                ["action", "record", "field"],
                "file",
                "Deleteing file but content is not file",
            ),
            "exp_event": (
                ["format"],
                "event",
                "Exporting events but content is not event",
            ),
            "exp_arm": (["format"], "arm", "Exporting arms but content is not arm"),
            "exp_fem": (
                ["format"],
                "formEventMapping",
                "Exporting form-event mappings but content != formEventMapping",
            ),
            "exp_next_id": (
                [],
                "generateNextRecordName",
                "Generating next record name but content is not generateNextRecordName",
            ),
            "exp_proj": (
                ["format"],
                "project",
                "Exporting project info but content is not project",
            ),
            "exp_user": (["format"], "user", "Exporting users but content is not user"),
            "exp_survey_participant_list": (
                ["instrument"],
                "participantList",
                "Exporting Survey Participant List but content != participantList",
            ),
            "exp_report": (
                ["report_id", "format"],
                "report",
                "Exporting Reports but content is not reports",
            ),
            "version": (
                ["format"],
                "version",
                "Requesting version but content != version",
            ),
        }
        extra, req_content, err_msg = valid_data[self.type]
        required.extend(extra)
        required = set(required)
        pl_keys = set(self.payload.keys())
        # if req is not subset of payload keys, this call is wrong
        if not set(required) <= pl_keys:
            # what is not in pl_keys?
            not_pre = required - pl_keys
            raise RCAPIError("Required keys: %s" % ", ".join(not_pre))
        # Check content, raise with err_msg if not good
        try:
            if self.payload["content"] != req_content:
                raise RCAPIError(err_msg)
        except KeyError as key_fail:
            raise RCAPIError("content not in payload") from key_fail

    def execute(self, **kwargs):
        """Execute the API request and return data

        Parameters
        ----------
        kwargs :
            passed to requests.Session.post()

        Returns
        -------
        response : list, str
            data object from JSON decoding process if format=='json',
            else return raw string (ie format=='csv'|'xml')
        """
        response = self.session.post(self.url, data=self.payload, **kwargs)
        # Raise if we need to
        self.raise_for_status(response)
        content = self.get_content(response)
        return content, response.headers

    # pylint: disable=invalid-name
    def get_content(self, r):
        """Abstraction for grabbing content from a returned response"""
        if self.type == "exp_file":
            # don't use the decoded r.text
            return r.content
        if self.type == "version":
            return r.content
        # pylint: disable=lost-exception
        if self.fmt == "json":
            content = {}
            # Decode
            try:
                # Watch out for bad/empty json
                content = json.loads(r.text, strict=False)
            except ValueError as e:
                if not self.expect_empty_json():
                    # reraise for requests that shouldn't send empty json
                    raise ValueError(e) from e
            finally:
                return content
        # pylint: enable=lost-exception
        return r.text

    # pylint: enable=invalid-name

    def expect_empty_json(self):
        """Some responses are known to send empty responses"""
        return self.type in ("imp_file", "del_file")

    # pylint: disable=invalid-name
    def raise_for_status(self, r):
        """Given a response, raise for bad status for certain actions

        Some redcap api methods don't return error messages
        that the user could test for or otherwise use. Therefore, we
        need to do the testing ourself

        Raising for everything wouldn't let the user see the
        (hopefully helpful) error message"""
        if self.type in ("metadata", "exp_file", "imp_file", "del_file"):
            r.raise_for_status()
        # see http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
        # specifically 10.5
        if 500 <= r.status_code < 600:
            raise RedcapError(r.content)

        if r.status_code == 400 and self.type == "exp_record":
            raise RedcapError(r.content)

    # pylint: enable=invalid-name
