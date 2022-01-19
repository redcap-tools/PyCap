#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=consider-using-f-string
"""

Low-level HTTP functionality

"""

import json
from typing import TYPE_CHECKING, List, Optional, Tuple, Union, overload

from typing_extensions import Literal, TypedDict

from requests import RequestException, Session

if TYPE_CHECKING:
    from io import TextIOWrapper

__author__ = "Scott Burns <scott.s.burns@gmail.com>"
__license__ = "MIT"
__copyright__ = "2014, Vanderbilt University"

RedcapError = RequestException

_session = Session()


class FileUpload(TypedDict):
    """Typing for the file upload API"""

    file: Tuple[str, "TextIOWrapper"]


class ErrorResponse(TypedDict):
    """Typing for a REDCap API error in a response"""

    error: str


class RCAPIError(Exception):
    """Errors corresponding to a misuse of the REDCap API"""


class RCRequest:
    """
    Private class wrapping the REDCap API. Decodes response from redcap
    and returns it.

    References
    ----------
    https://redcap.vanderbilt.edu/api/help/

    Users shouldn't really need to use this, the Project class is the
    biggest consumer.
    """

    def __init__(self, url, payload, req_type, session=_session):
        """
        Constructor

        Parameters
        ----------
        url : str
            REDCap API URL
        payload : dict
            key,values corresponding to the REDCap API
        req_type : str
            Used to validate payload contents against API
        """
        self.url = url
        self.payload = payload
        self.type = req_type
        self.session = session

        if req_type:
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
                ["action"],
                "record",
                "Deleting record but content is not record",
            ),
            "imp_record": (
                ["type", "overwriteBehavior", "data", "format"],
                "record",
                "Importing record but content is not record",
            ),
            "imp_metadata": (
                ["data", "format"],
                "metadata",
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
        if self.payload["content"] != req_content:
            raise RCAPIError(err_msg)

    @overload
    def execute(
        self,
        verify_ssl: Union[bool, str],
        return_headers: Literal[True],
        file: Optional[FileUpload],
    ) -> Tuple[Union[List[dict], str, int, bytes, ErrorResponse], dict]:
        ...

    @overload
    def execute(
        self,
        verify_ssl: Union[bool, str],
        return_headers: Literal[False],
        file: Optional[FileUpload],
    ) -> Union[List[dict], str, int, bytes, ErrorResponse]:
        ...

    @overload
    def execute(
        self,
        verify_ssl: Union[bool, str],
        return_headers: bool,
        file: Optional[FileUpload],
    ) -> Union[
        Tuple[Union[List[dict], str, int, bytes, ErrorResponse], dict],
        Union[List[dict], str, int, bytes, ErrorResponse],
    ]:
        ...

    def execute(
        self,
        verify_ssl: Union[bool, str],
        return_headers: bool,
        file: Optional[FileUpload],
    ):
        """Execute the API request and return data

        Args:
            verify_ssl: Verify SSL. Can also be a path to CA_BUNDLE
            return_headers:
                Whether or not response headers should be returned along
                with the request content
            file: A file object to send along with the request

        Returns:
            Data object from JSON decoding process if format=='json',
            else return raw string (ie format=='csv'|'xml')
        """
        response = self.session.post(
            self.url, data=self.payload, verify=verify_ssl, files=file
        )

        content = self.get_content(response)

        try:
            bad_request = "error" in content.keys()
        except AttributeError:
            # we're not dealing with an error dict
            bad_request = False

        if bad_request:
            raise RedcapError(bad_request)

        if return_headers:
            return content, response.headers

        return content

    # pylint: disable=invalid-name
    def get_content(self, r):
        """Abstraction for grabbing content from a returned response"""
        if self.type in ["exp_file", "version"]:
            # use bytes value
            content = r.content
        elif self.fmt == "json":
            content = {}
            # Decode
            try:
                # Watch out for bad/empty json
                content = json.loads(r.text, strict=False)
            except ValueError as e:
                if not self.expect_empty_json():
                    # reraise for requests that shouldn't send empty json
                    raise ValueError(e) from e
        else:
            # don't do anything to csv/xml strings
            content = r.text
        return content

    # pylint: enable=invalid-name

    def expect_empty_json(self):
        """Some responses are known to send empty responses"""
        return self.type in ("imp_file", "del_file")
