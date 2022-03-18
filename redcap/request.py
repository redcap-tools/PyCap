#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Low-level HTTP functionality"""

from collections import namedtuple
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    TypedDict,
    Union,
    overload,
)

from requests import RequestException, Response, Session

if TYPE_CHECKING:
    from io import TextIOWrapper

Json = List[Dict[str, Any]]
EmptyJson = List[dict]

__author__ = "Scott Burns <scott.s.burns@gmail.com>"
__license__ = "MIT"
__copyright__ = "2014, Vanderbilt University"

RedcapError = RequestException

_session = Session()


class FileUpload(TypedDict):
    """Typing for the file upload API"""

    file: Tuple[str, "TextIOWrapper"]


_ContentConfig = namedtuple("_ContentConfig", ["return_empty_json", "return_bytes"])


class _RCRequest:
    """
    Private class wrapping the REDCap API. Decodes response from redcap
    and returns it.
    """

    def __init__(
        self,
        url: str,
        payload: Dict[str, Any],
        config: _ContentConfig,
        session=_session,
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
        self.fmt = self._get_format_key(payload)

    @staticmethod
    def _get_format_key(
        payload: Dict[str, Any]
    ) -> Optional[Literal["json", "csv", "xml"]]:
        """Determine format of the response

        Args:
            payload: Payload to be sent in POST request

        Returns:
            The expected format of the response, if a format
            key was provided. Otherwise returns None to signal
            a non-standard response format e.g bytes, empty json, etc.

        Raises:
            ValueError: Unsupported format
        """
        if "returnFormat" in payload:
            fmt_key = "returnFormat"
        elif "format" in payload:
            fmt_key = "format"
        else:
            return None

        return payload[fmt_key]

    @overload
    @staticmethod
    def get_content(
        response: Response,
        format_type: None,
        return_empty_json: Literal[True],
        return_bytes: Literal[False],
    ) -> EmptyJson:
        ...

    @overload
    @staticmethod
    def get_content(
        response: Response,
        format_type: None,
        return_empty_json: Literal[False],
        return_bytes: Literal[True],
    ) -> bytes:
        ...

    @overload
    @staticmethod
    def get_content(
        response: Response,
        format_type: Literal["json"],
        return_empty_json: Literal[False],
        return_bytes: Literal[False],
    ) -> Union[Json, Dict[str, str]]:
        """This should return json, but might also return an error dict"""
        ...

    @overload
    @staticmethod
    def get_content(
        response: Response,
        format_type: Literal["csv", "xml"],
        return_empty_json: Literal[False],
        return_bytes: Literal[False],
    ) -> str:
        ...

    @staticmethod
    def get_content(
        response: Response,
        format_type: Optional[Literal["json", "csv", "xml"]],
        return_empty_json: bool,
        return_bytes: bool,
    ):
        """Abstraction for grabbing content from a returned response"""
        if return_bytes:
            return response.content

        if return_empty_json:
            return [{}]

        if format_type == "json":
            return response.json()

        # don't do anything to csv/xml strings
        return response.text

    @overload
    def execute(
        self,
        verify_ssl: Union[bool, str],
        return_headers: Literal[True],
        file: Optional[FileUpload],
    ) -> Tuple[Union[Json, str, bytes], dict]:
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
            format_type=self.fmt,
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
        # xml is the default returnFormat for error messages
        elif self.fmt == "xml" or self.fmt is None:
            bad_request = "<error>" in str(content).lower()

        if bad_request:
            raise RedcapError(content)

        if return_headers:
            return content, response.headers

        return content
