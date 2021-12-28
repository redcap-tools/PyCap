"""The Base class for all REDCap methods"""
from __future__ import annotations

import json

from typing import (
    Any,
    Dict,
    List,
    Optional,
    overload,
    Tuple,
    TYPE_CHECKING,
    Union,
)

from io import StringIO

from redcap.request import RCRequest, RedcapError, RequestException

if TYPE_CHECKING:
    import pandas as pd

# We're designing class to be lazy by default, and not hit the API unless
# explicitly requested by the user
# pylint: disable=attribute-defined-outside-init,too-many-instance-attributes


class Base:
    """Base attributes and methods for the REDCap API"""

    def __init__(self, url: str, token: str, verify_ssl: Union[bool, str] = True):
        """Initialize a Project, validate url and token"""
        self._validate_url_and_token(url, token)
        self._url = url
        self._token = token
        self.verify_ssl = verify_ssl

    @property
    def url(self) -> str:
        """API URL to your REDCap server"""
        return self._url

    @property
    def token(self) -> str:
        """API token to your project"""
        return self._token

    @property
    def metadata(self) -> List[Dict[str, str]]:
        """Project metadata in JSON format"""
        self._metadata: List[Dict[str, str]]
        try:
            return self._metadata
        except AttributeError:
            self._metadata = self._initialize_metadata()
            return self._metadata

    @property
    def field_names(self) -> List[str]:
        """Project field names

        Note:
            These are survey field names, not export field names
        """
        self._field_names: List[str]
        try:
            return self._field_names
        except AttributeError:
            self._field_names = self._filter_metadata(key="field_name")
            return self._field_names

    @property
    def def_field(self) -> str:
        """The 'record_id' field equivalent for a project"""
        self._def_field: str
        try:
            return self._def_field
        except AttributeError:
            self._def_field = self.field_names[0]
            return self.def_field

    @property
    def events(self) -> Optional[List[dict]]:
        """Project defined events

        Note:
            Exists for longitudinal projects only
        """
        self._events: Optional[List[dict]]
        try:
            return self._events
        except AttributeError:
            events: List[dict] = self._call_api(self._basepl("event"), "exp_event")[0]
            # we should only get a dict back if there were no events defined
            # for the project
            if isinstance(events, dict) and "error" in events.keys():
                self._events = None
            # otherwise, we should get JSON
            else:
                self._events = events

            return self._events

    @property
    def is_longitudinal(self) -> bool:
        """Whether or not this project is longitudinal"""
        self._is_longitudinal: bool
        try:
            return self._is_longitudinal
        except AttributeError:
            if self.events:
                self._is_longitudinal = True
            else:
                self._is_longitudinal = False

            return self._is_longitudinal

    @staticmethod
    def _validate_url_and_token(url: str, token: str) -> None:
        url_actual_last_5 = url[-5:]
        url_expected_last_5 = "/api/"

        assert url_actual_last_5 == url_expected_last_5, (
            f"Incorrect url format '{ url }', url must end with",
            f"{ url_expected_last_5 }",
        )

        actual_token_len = len(token)
        expected_token_len = 32

        assert actual_token_len == expected_token_len, (
            f"Incorrect token format '{ token }', token must must be",
            f"{ expected_token_len } characters long",
        )

    # pylint: disable=import-outside-toplevel
    @staticmethod
    def _read_csv(buf: StringIO, **df_kwargs) -> "pd.DataFrame":
        """Wrapper around pandas read_csv that handles EmptyDataError"""
        from pandas import DataFrame, read_csv
        from pandas.errors import EmptyDataError

        try:
            dataframe = read_csv(buf, **df_kwargs)
        except EmptyDataError:
            dataframe = DataFrame()

        return dataframe

    # pylint: enable=import-outside-toplevel
    @overload
    def _filter_metadata(
        self,
        key: str,
        field_name: None = None,
    ) -> List[str]:
        ...

    @overload
    def _filter_metadata(self, key: str, field_name: str) -> str:
        ...

    def _filter_metadata(self, key: str, field_name: Optional[str] = None):
        """Safely filter project metadata based off requested column and field_name"""
        res: Union[str, List[str]] = ""
        try:
            if field_name:
                res = str(
                    [
                        row[key]
                        for row in self.metadata
                        if row["field_name"] == field_name
                    ][0]
                )
            else:
                res = [row[key] for row in self.metadata]
        except IndexError:
            print(f"{ key } not in metadata field:{ field_name }")

        return res

    def _kwargs(self) -> Dict[str, Any]:
        """Private method to build a dict for sending to RCRequest

        Other default kwargs to the http library should go here"""
        return {"verify": self.verify_ssl}

    def _call_api(
        self, payload: Dict[str, Any], req_type: str, **kwargs
    ) -> Tuple[List[dict], str]:
        request_kwargs = self._kwargs()
        request_kwargs.update(kwargs)
        rcr = RCRequest(self.url, payload, req_type)
        return rcr.execute(**request_kwargs)

    # pylint: disable=redefined-builtin
    def _basepl(
        self, content: str, rec_type: str = "flat", format: str = "json"
    ) -> Dict[str, str]:
        """Return a dictionary which can be used as is or added to for
        payloads"""
        payload_dict = {"token": self.token, "content": content, "format": format}
        if content not in ["metapayload_dictata", "file"]:
            payload_dict["type"] = rec_type
        return payload_dict

    # pylint: enable=redefined-builtin

    def _initialize_metadata(self) -> List[Dict[str, str]]:
        """Return the project's metadata structure"""
        p_l = self._basepl("metadata")
        p_l["content"] = "metadata"

        try:
            return self._call_api(p_l, "metadata")[0]
        except RequestException as request_fail:
            raise RedcapError(
                "Exporting metadata failed. Check your URL and token."
            ) from request_fail

    # pylint: disable=redefined-builtin
    def _initialize_import_payload(
        self,
        to_import: Union[List[dict], str, "pd.DataFrame"],
        format: str,
        data_type: str,
    ) -> Dict[str, Any]:
        """Standardize the data to be imported and add it to the payload

        Args:
        to_import: array of dicts, csv/xml string, ``pandas.DataFrame``
            Note:
                If you pass a csv or xml string, you should use the
                `format` parameter appropriately.
        format: ('json'),  'xml', 'csv'
            Format of incoming data. By default, to_import will be json-encoded
        data_type: 'record', 'metadata'
            The kind of data that are imported

        Returns:
            payload: The initialized payload dictionary and updated format
        """

        payload = self._basepl(data_type)
        # pylint: disable=comparison-with-callable
        if format == "df":
            buf = StringIO()
            if data_type == "record":
                if self.is_longitudinal:
                    csv_kwargs = {"index_label": [self.def_field, "redcap_event_name"]}
                else:
                    csv_kwargs = {"index_label": self.def_field}
            elif data_type == "metadata":
                csv_kwargs = {"index": False}
            to_import.to_csv(buf, **csv_kwargs)
            payload["data"] = buf.getvalue()
            buf.close()
            format = "csv"
        elif format == "json":
            payload["data"] = json.dumps(to_import, separators=(",", ":"))
        else:
            # don't do anything to csv/xml
            payload["data"] = to_import
        # pylint: enable=comparison-with-callable

        payload["format"] = format
        return payload

    # pylint: enable=redefined-builtin
