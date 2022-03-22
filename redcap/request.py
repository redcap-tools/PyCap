#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Low-level HTTP functionality"""

import asyncio
from collections import namedtuple
from typing import TYPE_CHECKING, Any, Coroutine, Dict, List, Optional, Tuple, Union, overload

from typing_extensions import Literal, TypedDict

from coroutine import _RCCorutine

if TYPE_CHECKING:
    from io import TextIOWrapper

Json = List[Dict[str, Any]]
EmptyJson = List[dict]

__author__ = "Scott Burns <scott.s.burns@gmail.com>"
__license__ = "MIT"
__copyright__ = "2014, Vanderbilt University"

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
        def_field: str,
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
        self.fmt = self._get_format_key(payload)
        self.def_field = def_field

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
    def execute(
        self,
        verify_ssl: Union[bool, str],
        return_headers: Literal[True],
        file: Optional[FileUpload],
        coroutine: bool,
        sleep_time: int,
        chunks: int,
    ) -> Tuple[Union[Json, str, bytes], dict]:
        ...

    @overload
    def execute(
        self,
        verify_ssl: Union[bool, str],
        return_headers: Literal[False],
        file: Optional[FileUpload],
        coroutine: bool,
        sleep_time: int,
        chunks: int,
    ) -> Union[List[Dict[str, Any]], str, bytes]:
        ...

    @overload
    def execute(
        self,
        verify_ssl: Union[bool, str],
        return_headers: Literal[False],
        file: Optional[FileUpload],
        coroutine: bool,
        sleep_time: int,
        chunks: int,
    ) -> Coroutine:
        ...

    def execute(
        self,
        verify_ssl: Union[bool, str],
        return_headers: bool,
        file: Optional[FileUpload],
        coroutine: bool,
        sleep_time: int,
        chunks: int,
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

        request_coroutine = _RCCorutine(self.url,
            self.payload,
            self.fmt, verify_ssl,
            self.def_field,
            return_headers,
            file,
            sleep_time, 
            chunks
        )

        if coroutine:
            return request_coroutine.run()
        else:
            return asyncio.run(request_coroutine.run())
