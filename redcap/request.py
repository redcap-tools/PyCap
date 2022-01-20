#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=consider-using-f-string
"""

Low-level HTTP functionality

"""

from collections import namedtuple
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union, overload

from typing_extensions import Literal, TypedDict

from requests import RequestException, Response, Session

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


class RCAPIError(Exception):
    """Errors corresponding to a misuse of the REDCap API"""


RCConfig = namedtuple("RCConfig", ["return_empty_json", "return_bytes"])


class _RCRequest:
    """
    Private class wrapping the REDCap API. Decodes response from redcap
    and returns it.
    """

    def __init__(
        self, url: str, payload: Dict[str, Any], config: RCConfig, session=_session
    ):
        """Constructor

        Args:
            url: REDCap API URL
            payload: Keys and values corresponding to the REDCap API
            config: Configuration values for getting content
        """
        self.url = url
        self.payload = payload
        self.config = config
        self.session = session

        fmt_key = "returnFormat" if "returnFormat" in payload else "format"
        fmt = payload[fmt_key]

        if fmt in ["json", "csv", "xml"]:
            self.fmt = fmt
        else:
            raise ValueError(f"Unsupported format: { fmt }")

    @overload
    @staticmethod
    def get_content(
        response: Response,
        req_format: Literal["json", "csv", "xml"],
        return_empty_json: Literal[True],
        return_bytes: Literal[False],
    ) -> List[dict]:
        ...

    @overload
    @staticmethod
    def get_content(
        response: Response,
        req_format: Literal["json", "csv", "xml"],
        return_empty_json: Literal[False],
        return_bytes: Literal[True],
    ) -> bytes:
        ...

    @overload
    @staticmethod
    def get_content(
        response: Response,
        req_format: Literal["json"],
        return_empty_json: Literal[False],
        return_bytes: Literal[False],
    ) -> Union[List[Dict[str, Any]], Dict[str, str]]:
        """This should return json, but might also return an error dict"""
        ...

    @overload
    @staticmethod
    def get_content(
        response: Response,
        req_format: Literal["csv", "xml"],
        return_empty_json: Literal[False],
        return_bytes: Literal[False],
    ) -> str:
        ...

    @staticmethod
    def get_content(
        response: Response,
        req_format: Literal["json", "csv", "xml"],
        return_empty_json: bool,
        return_bytes: bool,
    ):
        """Abstraction for grabbing content from a returned response"""
        if return_bytes:
            return response.content

        if return_empty_json:
            return [{}]

        if req_format == "json":
            return response.json()

        # don't do anything to csv/xml strings
        return response.text

    @overload
    def execute(
        self,
        verify_ssl: Union[bool, str],
        return_headers: Literal[True],
        file: Optional[FileUpload],
    ) -> Tuple[Union[List[Dict[str, Any]], str, bytes], dict]:
        ...

    @overload
    def execute(
        self,
        verify_ssl: Union[bool, str],
        return_headers: Literal[False],
        file: Optional[FileUpload],
    ) -> Union[List[Dict[str, Any]], str, bytes]:
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

        Raises:
            RedcapError:
                Badly formed request i.e record doesn't
                exist, field doesn't exist, etc.
        """
        response = self.session.post(
            self.url, data=self.payload, verify=verify_ssl, files=file
        )

        content = self.get_content(
            response,
            req_format=self.fmt,
            return_empty_json=self.config.return_empty_json,
            return_bytes=self.config.return_bytes,
        )

        if self.fmt == "json":
            try:
                bad_request = "error" in content.keys()
            except AttributeError:
                # we're not dealing with an error dict
                bad_request = False
        elif self.fmt == "csv":
            bad_request = content.lower().startswith("error:")
        elif self.fmt == "xml":
            bad_request = "<error>" in content.lower()

        if bad_request:
            raise RedcapError(content)

        if return_headers:
            return content, response.headers

        return content
